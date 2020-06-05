import tensorflow as tf
import os
import numpy as np
from datetime import datetime
from sklearn.metrics import f1_score
from train_util import *
from augmentation.augment_data import *
from pipeline import *

class Trainer:
    def __init__(self, args, model):
        # Paths
        self.args = args
        self.logdir = os.path.join(args.base, args.logdir)
        self.fold = args.fold
        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)
        self.model_save_path = os.path.join(args.base, args.model_path)
        self.model_save_period = 10

        self.train_data = os.path.join(args.base, args.train_datapath)
        self.test_data = os.path.join(args.base, args.test_datapath)
        self.write_log(f'Fold: {self.fold}')

        # Data processing
        self.decode_record = args.decode_record
        self.record_shape = args.record_shape

        # General parameters
        self.test_evaluation_period = 1
        self.num_batches = int(args.num_batches)

        # Network parameters
        self.model = model
        self.attention = args.attention
        self.feature_shape = args.feature_shape
        self.batch_size = args.batch_size
        self.test_size = min(self.batch_size, len(list(tf.python_io.tf_record_iterator(self.test_data))))

        # Hyperparameters
        self.weight_decay = 0# 1e-4
        self.dropout_train_prob = 0.5
        starter_learning_rate = 5e-6
        self.global_step = tf.Variable(0, trainable=False)
        self.learning_rate = starter_learning_rate

        # Logging
        self.best = {'batch': None, 'report': None, 'preds': None, 'loss': float("inf")}

    def write_log(self, line):
        with open(os.path.join(self.logdir, 'LOG'), 'a') as levels:
            levels.write(f'{line}\n')

    def update_stats(self, batch, loss, preds, labels):
        if loss < self.best['loss']:
            self.best['batch'] = batch
            self.best['loss'] = loss
            self.best['preds'] = preds
            self.best['labels'] = labels
            self.best['report'] = report(labels, preds)

    def create_summary(self, name, graph):
        path = os.path.join(self.logdir, f'fold{self.fold}', name)
        return tf.summary.FileWriter(path, graph)

    def log_metrics(self, sess, batch, writer, accuracy, f1):
        a_s = sess.run(self.accuracy_summary, feed_dict={self.accuracy_placeholder: accuracy})
        writer.add_summary(a_s, int(batch))

        f1_s = sess.run(self.f1_summary, feed_dict={self.f1_placeholder: f1})
        writer.add_summary(f1_s, int(batch))

    def train(self):
        # Model saving
        # tf.reset_default_graph()

        # Dataset pipeline
        pipeline = Pipeline(self.decode_record, self.record_shape)
        iterator = pipeline.create_train(self.train_data, self.batch_size)
        iterator_te = pipeline.create_test(self.test_data, self.test_size)
        iterator_next, iterator_te_next = iterator.get_next(), iterator_te.get_next()

        # Initialise classification network
        network = self.model(self.feature_shape, self.global_step, lr=self.learning_rate,
                            weight_decay=self.weight_decay, attention=self.attention)

        # Initialise augmentation
        augmentor = Augmentor(self.feature_shape)

        # Summaries
        self.accuracy_placeholder = tf.placeholder(tf.float32)
        self.accuracy_summary = tf.summary.scalar('accuracy', self.accuracy_placeholder)
        self.f1_placeholder = tf.placeholder(tf.float32)
        self.f1_summary = tf.summary.scalar('f1', self.f1_placeholder)

        # Train
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        config.allow_soft_placement = True
        with tf.Session(config=config) as sess:
            # Initialise variables
            tf.global_variables_initializer().run()
            sess.run(iterator.initializer)
            sess.run(iterator_te.initializer)

            # Summary writers
            summary_writer_tr = self.create_summary('train', sess.graph)
            summary_writer_te = self.create_summary('test', sess.graph)
            saver = tf.train.Saver()

            train_accuracies = []
            for batch in range(self.num_batches):
                # Evaluate performance on test set at intervals
                if batch % self.test_evaluation_period == 0:
                    summary_te, average_accuracy, overall_loss, preds, all_labels = test_accuracy(sess, network, iterator_te, iterator_te_next, self.feature_shape)
                    summary_writer_te.add_summary(summary_te, int(batch))
                    self.update_stats(batch, overall_loss, preds, all_labels)
                    self.log_metrics(sess, batch, summary_writer_te, average_accuracy, f1_score(all_labels, preds))

                # Train the network
                batch_images, batch_labels = sess.run(iterator_next)
                aug_batch_images = augmentor.augment_batch(batch_images)
                binary_labels = binarise_labels(batch_labels)

                _, loss, summary, binary_preds = sess.run([network.train_op, network.summary_loss, network.summary, network.predictions],
                                            feed_dict={network.batch_features: aug_batch_images,
                                                       network.batch_labels: parse_labels(binary_labels),
                                                       network.dropout_prob: self.dropout_train_prob})

                # Summaries and statistics
                print('-------- Train epoch %d.%d --------' % (batch // self.test_evaluation_period, batch % self.test_evaluation_period))
                summary_writer_tr.add_summary(summary, int(batch))

                train_accuracies.append(accuracy(batch_labels, binary_preds))
                running_accuracy = np.average(train_accuracies[-self.test_evaluation_period:])

                self.log_metrics(sess, batch, summary_writer_tr, running_accuracy, f1_score(binary_labels, binary_preds))

                print_statistics(loss, binary_labels, binary_preds)

                # Save model
                if batch % self.model_save_period == 0:
                    saver.save(sess, self.model_save_path)
                    print('Model saved!')

            print('Training finished!')
            self.write_log(f'Best loss (epoch {self.best["batch"]}): {round(self.best["loss"], 3)}')
            self.write_log(f'with predictions: {self.best["preds"]}')
            self.write_log(f'of labels:        {self.best["labels"]}')
            self.write_log(self.best["report"])
            self.write_log('')
