import SimpleITK as sitk
import os
import shutil
import tensorflow as tf
import pandas as pd
import time
import matplotlib.pyplot as plt

from dltk.io.augmentation import *
from dltk.io.preprocessing import *

data_path = 'copied_data/clean_nifti/'
data = os.listdir(data_path)

# Clear previous logs (temporary)
logdir = '/vol/bitbucket/rh2515/CrohnsDisease/logdir'
# shutil.rmtree(logdir, ignore_errors=True)

with tf.Session() as sess:
    # Tensorboard
    summary_writer = tf.summary.FileWriter(logdir, sess.graph)

    image = tf.placeholder(tf.float32)
    tf.summary.image("Image", image[np.newaxis, ..., np.newaxis])
    tf.summary.histogram("Whitened Image", image)

    # Collect summaries
    summaries = tf.summary.merge_all()

    with tf.name_scope('Images'):
        for i, d in enumerate(data):
            t1_fn = os.path.join(data_path, d)

            # Read image
            f"(Reading data ${data_path})"
            sitk_t1 = sitk.ReadImage(t1_fn)
            t1 = sitk.GetArrayFromImage(sitk_t1)

            # Normalise the image to zero mean/unit std dev:
            t1 = whitening(t1)

            # Other
            print(t1.shape)
            # imgplot = plt.imshow(t1[300])
            # plt.show()
            s = sess.run(summaries, feed_dict={image: t1[300]})

            summary_writer.add_summary(s, global_step=i)
