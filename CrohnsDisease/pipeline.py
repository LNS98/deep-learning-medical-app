import tensorflow as tf

class Pipeline:
    def __init__(self, decode, volume_shape=(5, 256, 256)):
        self.decode = decode
        self.volume_shape = volume_shape

    def create_train(self, train_data, batch_size=10):
        # Train pipeline
        dataset = tf.data.TFRecordDataset(train_data).map(self.decode)
        dataset = dataset.repeat(None)
        dataset = dataset.shuffle(4 * batch_size, reshuffle_each_iteration=True)
        dataset = dataset.batch(batch_size)
        dataset = dataset.prefetch(1)

        # Dataset iterator
        iterator = dataset.make_initializable_iterator()
        return iterator

    def create_test(self, test_data, test_size=10):
        # Test pipeline
        dataset_te = tf.data.TFRecordDataset(test_data).map(self.decode)
        dataset_te = dataset_te.batch(test_size)
        iterator_te = dataset_te.make_initializable_iterator()

        return iterator_te
