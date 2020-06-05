import tensorflow as tf

class Classifier:
    def __init__(self, input_shape, lr, weight_decay, global_step):
        self.batch_features = tf.placeholder(tf.float32, shape=(None,) + input_shape)
        self.batch_labels = tf.placeholder(tf.float64)

        # Initialise Model
        self.lr = lr
        self.weight_decay = weight_decay
        self.global_step = global_step

    def build(self, net_output):
        self.logits = net_output
        self.probabilities = tf.nn.softmax(self.logits)
        self.predictions = tf.argmax(tf.nn.softmax(net_output), axis=1)

        self.ground_truth = tf.cast(self.batch_labels, tf.float32)
        ground_truth = tf.expand_dims(self.ground_truth, 1)

        cross_entropy_loss = tf.nn.softmax_cross_entropy_with_logits_v2(labels=self.ground_truth, logits=net_output)
        l2_loss = tf.add_n([tf.nn.l2_loss(v) for v in tf.trainable_variables()])
        loss = cross_entropy_loss + self.weight_decay * l2_loss

        optimiser = tf.train.AdamOptimizer(learning_rate=self.lr)
        self.train_op = optimiser.minimize(loss, global_step=self.global_step, colocate_gradients_with_ops=True)

        self.summary_loss = tf.reduce_mean(loss)
        tf.summary.scalar("learning_rate", self.lr)
        tf.summary.scalar("loss", self.summary_loss)
        self.summary = tf.summary.merge_all()
