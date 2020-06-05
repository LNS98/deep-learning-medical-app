import os
import tensorflow as tf
import SimpleITK as sitk

from train_util import *
from pipeline import *
from preprocessing.metadata import Patient
from preprocessing.preprocess import Preprocessor
from augmentation.augment_data import process

class Infer():
    def __init__(self, args, model):
        self.args = args
        self.global_step = tf.Variable(0, trainable=False)

        self.network = model(args.feature_shape, self.global_step, attention=args.attention)
        self.saver = tf.train.Saver()
        self.model_save_path = os.path.join(args.base, args.model_path)
        print('Loaded network from', self.model_save_path)

    def test(self, test_data):
        test_size = len(list(tf.python_io.tf_record_iterator(test_data)))

        # Dataset pipeline
        pipeline = Pipeline(self.args.decode_record, self.args.record_shape)

        iterator_te = pipeline.create_test(test_data, test_size)
        iterator_te_next = iterator_te.get_next()

        with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
            sess.run(iterator_te.initializer)
            self.saver.restore(sess, self.model_save_path)

            test_accuracy(sess, self.network, iterator_te, iterator_te_next, self.args.feature_shape)

    def infer(self, axial_path, coords, record_shape, feature_shape): # what are the record_shape and feature_shape
        print('Inferring prediction from image:', axial_path, 'at coordinates', coords)

        patient = Patient('A', 36)
        # patient.set_paths('/vol/bitbucket/rh2515/MRI_Crohns/A/A1 Axial T2.nii')

        patient.set_paths(axial_path) # ADDED BY US

        patient.set_ileum_coordinates(coords)
        patient.load_image_data()
        classes = {0: 'healthy', 1: 'abnormal (Crohn\'s)'} # why not 5 classes?

        preprocessor = Preprocessor(constant_volume_size=[record_shape[1], record_shape[2], record_shape[0]])
        [patient] = preprocessor.process([patient], ileum_crop=True, region_grow_crop=False, statistical_region_crop=False)

        # tf.reset_default_graph()
        with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:

            saver = tf.train.import_meta_graph(self.model_save_path + 'model_save2.meta')
            saver.restore(sess, self.model_save_path + 'model_save2')

            processed_image = process(sitk.GetArrayFromImage(patient.axial_image), out_dims=feature_shape)
            probabilities, predictions = sess.run([self.network.probabilities, self.network.predictions], # signature of conv layer
                    feed_dict={self.network.batch_features: [processed_image]})
            print('Patient is predicted to be', classes[predictions[0]], 'with probability', round(probabilities[0][predictions[0]],3))


#
# if __name__ == "__main__":
#     Infer().infer()
