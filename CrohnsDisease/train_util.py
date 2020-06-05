from sklearn.metrics import classification_report
from dltk.io.preprocessing import *

import tensorflow as tf
import numpy as np

def generate_decode_function(feature_shape, feature_name):
    def decode_record(serialized_example):
        feature_key = f'train/{feature_name}'
        features = tf.parse_single_example(
            serialized_example,
            features={feature_key: tf.FixedLenFeature(feature_shape, tf.float32),
                      'train/label': tf.FixedLenFeature([], tf.int64),
                      'data/index': tf.FixedLenFeature([], tf.int64)})

        return features[feature_key], features['train/label']#, features['data/index']
    return decode_record

def binarise_labels(labels):
    return [int(label > 0) for label in labels]

def parse_labels(labels):
    return [[0, 1] if level > 0 else [1, 0] for level in labels]

def parse_test_features(features, feature_shape):
    parsed_features = []
    for i, feature in enumerate(features):
        diff = (np.array(feature.shape) - np.array(feature_shape)).astype(int)
        a = [int(round(d / 2)) for d in diff]
        parsed_features.append(whitening(feature[a[0]:-(diff[0]-a[0]), a[1]:-(diff[1]-a[1]), a[2]:-(diff[2]-a[2])]))
    return np.array(parsed_features)

def prediction_class_balance(preds):
    return np.sum(preds) / len(preds)

def accuracy(true_labels, binary_preds):
    tl_string = ''.join(str(x) for x in true_labels)
    binary_labels = binarise_labels(true_labels)
    bl_string = ''.join(str(x) for x in binary_labels)
    p_string = ''.join(str(x) for x in binary_preds)
    print(f'True Label:        {tl_string}')
    print(f'Binary Label:      {bl_string}')
    print(f'Binary Prediction: {p_string}')
    return np.sum(np.array(binary_labels) == np.array(binary_preds)) / len(binary_labels)

def report(labels, preds):
    if len(set(preds)) > 1:
        return classification_report(labels, preds, target_names=['healthy', 'abnormal'])
    return 'Only one class predicted'

def print_statistics(loss, labels, preds):
    print('Loss:               ', loss)
    print('Prediction balance: ', prediction_class_balance(preds))
    print(report(labels, preds))

# Test
def test_accuracy(sess, network, iterator_te, iterator_te_next, feature_shape):
    accuracies, all_labels, all_preds, losses = [], [], [], []
    summary_te = None

    # Iterate over whole test set
    print('Test statistics')
    while (True):
        try:
            batch_images, batch_labels = sess.run(iterator_te_next)
            binary_labels = binarise_labels(batch_labels)
            parsed_batch_features = parse_test_features(batch_images, feature_shape)

            loss_te, summary_te, preds = sess.run([network.summary_loss, network.summary, network.predictions],
                                            feed_dict={network.batch_features: parsed_batch_features,
                                                       network.batch_labels: parse_labels(binary_labels)})
            losses += [loss_te] * len(batch_labels)
            all_preds += preds.tolist()
            all_labels += batch_labels.tolist()

        except tf.errors.OutOfRangeError:
            sess.run(iterator_te.initializer)
            overall_accuracy = accuracy(all_labels, all_preds)
            overall_loss = np.average(losses)

            print_statistics(overall_loss, binarise_labels(all_labels), all_preds)

            return summary_te, overall_accuracy, overall_loss, all_preds, binarise_labels(all_labels)
