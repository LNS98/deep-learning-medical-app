import tensorflow as tf
from model.classifier import Classifier
from model.attention_layer import GridAttentionBlock
Conv3D = tf.keras.layers.Conv3D

def make_parallel(fn, num_gpus, **kwargs):
    in_splits = {}
    for k, v in kwargs.items():
        in_splits[k] = tf.split(v, num_gpus)

    out_split = []
    for i in range(num_gpus):
        with tf.device(tf.DeviceSpec(device_type="GPU", device_index=i)):
            with tf.variable_scope(tf.get_variable_scope(), reuse=tf.AUTO_REUSE):
                out_split.append(fn(**{k : v[i] for k, v in in_splits.items()}))

    return tf.concat(out_split, axis=0)

class ResNet3D(Classifier):
    # ResNet block with mirror padding
    def block(self, net, out_channels, shortcut_f, filter_dims=3, filter_strides=2,
                  padding='VALID', act_f=tf.nn.relu):


        shortcut = shortcut_f(net, out_channels, filter_strides)
        net = tf.pad(net, tf.constant([[0, 0], [1, 1], [1, 1], [1, 1], [0, 0]]))

        net = Conv3D(out_channels, filter_dims, strides=filter_strides, padding=padding, data_format="channels_last")(net)
        net = tf.layers.batch_normalization(net, axis=4)
        net = tf.nn.relu(net)

        net = tf.pad(net, tf.constant([[0, 0],  [1, 1], [1, 1], [1, 1], [0, 0]]))
        net = Conv3D(out_channels, filter_dims, strides=1, padding=padding, data_format="channels_last")(net)
        net = net + shortcut
        net = tf.layers.batch_normalization(net, axis=4)
        net = tf.nn.relu(net)

        return net

    def dense_layer(self, net, n_outputs, act_f = tf.nn.relu, dropout=True):
        net = tf.layers.dense(net, n_outputs)
        if act_f != None:
            net = act_f(net)
        if dropout:
            net = tf.nn.dropout(net, self.dropout_prob)
        return net

    def n_convs(self, net, specs):
        for channels, stride in specs:
            net = self.block(net, channels, self.p_s, filter_strides=stride)
            print(net.shape)
        return net

    # Classification module
    def classify(self, net):
        net = tf.layers.flatten(net)
        net = self.dense_layer(net, 2, act_f=None, dropout=True)
        return net

    def build_ti_net(self, input, attention=False):
        in_pic = input[0][0][input.shape[2] // 3]
        tf.summary.image('original_slice', tf.expand_dims(tf.expand_dims(in_pic, axis=0), axis=3), max_outputs=10)

        # 3D ResNet specification
        conv1 = self.n_convs(input, [(64, 2), (64, 1), (64, 1)])
        conv2 = self.n_convs(conv1, [(128, 2), (128, 1), (128, 1)])
        conv3 = self.n_convs(conv2, [(256, 2), (256, 1), (256, 1)])
        pooled = tf.layers.average_pooling3d(conv3, conv3.shape[1:-1], 1, padding='valid', data_format='channels_last')

        logits = self.classify(pooled)

        if attention:
            attention_layer = GridAttentionBlock(conv1.shape[4])
            compatability = attention_layer(conv1, conv3)
            attention_logits = self.classify(compatability)

            # Weight prediction of original network with prediction from attention layer
            logits = tf.reduce_mean(tf.stack([logits, attention_logits], 0), 0)

        return logits

    def __init__(self, input_shape, global_step, lr=5e-6, weight_decay=0, attention=False):
        super().__init__(input_shape, lr, weight_decay, global_step)

        def projection_shortcut(net, out_channels, filter_strides, padding='VALID'):
            return Conv3D(out_channels, 1, strides=filter_strides, padding=padding, data_format="channels_last")(net)
        self.p_s = projection_shortcut

        self.dropout_prob = tf.placeholder_with_default(1.0, shape=())

        net = tf.expand_dims(self.batch_features, axis=1)

        # here should change the dimensions
        net = tf.transpose(net, [0, 2, 3, 4, 1])

        # net = make_parallel(self.build_long_net, 1, input=net)
        # net = make_parallel(self.build_ti_net, 1, input=net)
        net = self.build_ti_net(net, attention=attention)

        self.build(net)
