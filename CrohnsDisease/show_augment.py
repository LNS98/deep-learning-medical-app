import tensorflow as tf
from scripts.show import *
from pipeline import Pipeline
from augmentation.augment_data import *
from main_util import *

train_data = '/vol/gpudata/rh2515/MRI_Crohns/tfrecords/ti_n100_k4_large/axial_t2_only_cropped_train_fold0.tfrecords'
test_data = '/vol/gpudata/rh2515/MRI_Crohns/tfrecords/ti_n100_k4_large/axial_t2_only_cropped_test_fold0.tfrecords'
# record_shape=(42,116,140)
# feature_shape=(32,88,112)
record_shape=(30,96,96)
feature_shape=(24,80,80)

# Dataset pipeline
decode_record = generate_decode_function(record_shape, 'axial_t2')
pipeline = Pipeline(decode_record, train_data, test_data)
iterator, iterator_te = pipeline.create(volume_shape=record_shape, batch_size=74, test_size=20)
features, labels = iterator.get_next()

# Augmentation
augmentor = Augmentor(feature_shape)

with tf.Session() as sess:
    # Initialise
    sess.run(iterator.initializer)
    sess.run(iterator_te.initializer)

    batch_images, batch_labels = sess.run([features, labels])

    aug_batch_images = augmentor.augment_batch(np.copy(batch_images))

    a = 0

    for vol, aug_vol in zip(batch_images, aug_batch_images):
        slice = int(aug_vol.shape[0] / 2)
        slice = 0
        img, aug_img = vol[slice], aug_vol[slice]
        fig=plt.figure(figsize=(1, 2))
        fig.set_size_inches(10, 5)

        fig.add_subplot(1, 2, 1)
        plt.imshow(img, cmap='gray')
        plt.title('Original')
        fig.add_subplot(1, 2, 2)
        plt.imshow(aug_img, cmap='gray')
        plt.title('Augmented')
        plt.savefig(f'images/foo{a}.png')
        a += 1
