import tensorflow as tf
import numpy as np
Conv3D = tf.keras.layers.Conv3D

def image_summary(name, a_m, stretch=True):
    im = tf.expand_dims(tf.expand_dims(a_m, axis=0), axis=3)
    if stretch:
        im = tf.divide(tf.subtract(im, tf.reduce_min(im)), tf.reduce_max(im)) * 255
    tf.summary.image(name, im, max_outputs=1)

class GridAttentionBlock():
    # f: features, g: gating signal
    def __init__(self, in_channels, inter_channels=None):
        self.in_channels = in_channels

        self.inter_channels = inter_channels
        if self.inter_channels is None:
            self.inter_channels = in_channels // 2

    def __call__(self, f, g):

        # Compute compatability and then normalised attentoin
        mapped_f = Conv3D(self.inter_channels.value, 1, strides=1, padding='SAME', data_format="channels_last")(f)
        scale = [f.shape[i] // g.shape[i] for i in range(1, 4)]
        mapped_g = Conv3D(self.inter_channels.value, 1, strides=1, padding='SAME', data_format="channels_last")(g)
        upsampled_mapped_g = tf.keras.layers.UpSampling3D(scale, data_format='channels_last')(mapped_g)

        combined = tf.nn.relu(tf.keras.layers.Add()([mapped_f, upsampled_mapped_g]))
        attention = Conv3D(self.inter_channels.value, 1, strides=1, padding='SAME', data_format="channels_last")(combined)

        shifted_attention = tf.math.subtract(attention, tf.math.reduce_min(attention))
        normalised_attention = tf.math.divide(shifted_attention, tf.math.reduce_sum(shifted_attention))

        # Attend normalised attention onto features
        attended_attention = tf.math.multiply(normalised_attention, mapped_f)

        # Logging
        image_summary('feature', f[0, f.shape[1] // 3, :, :, 0])
        image_summary('gate', g[0, g.shape[1] // 3, :, :, 0])

        tf.summary.scalar('max_diff_attention', tf.math.reduce_max(normalised_attention) - tf.math.reduce_min(normalised_attention))
        image_summary('normalised_attenton', normalised_attention[0, normalised_attention.shape[1] // 3, :, :, 0])
        image_summary('attended_attention', attended_attention[0, attended_attention.shape[1] // 3,:, :, 0])

        return attended_attention
