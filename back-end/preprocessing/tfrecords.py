import os
import tensorflow as tf
import SimpleITK as sitk
import random
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def _float_feature(value):
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))

def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def tfrecord_name(set, suffix=''):
    return f'{suffix}_{set}.tfrecords'

def get(ls, ixs):
    return [ls[i] for i in ixs]

class TFRecordGenerator:
    def __init__(self, out_path, suffix):
        self.out_path = out_path
        self.suffix = suffix

        if not os.path.exists(self.out_path):
            os.makedirs(self.out_path)

        self.write_log(f'Dataset created: {str(datetime.now())}')

    def write_log(self, line):
        with open(os.path.join(self.out_path, 'METADATA'), 'a') as levels:
            levels.write(f'{line}\n')

    def _generate_tfrecords(self, patients, set='train', fold=''):
        writer = tf.python_io.TFRecordWriter(os.path.join(self.out_path, tfrecord_name(f'{set}_{fold}', self.suffix)))

        abnormal = [p.index for p in patients if p.group == 'A']
        healthy = [p.index for p in patients if p.group == 'I']
        self.write_log(f'{set} set, fold {fold}:')
        self.write_log(f'A - {abnormal}')
        self.write_log(f'I - {healthy}')
        self.write_log([p.severity for p in patients])

        for i, patient in enumerate(patients):
            try:
                image_array = sitk.GetArrayFromImage(patient.axial_image)
                feature = { 'train/label': _int64_feature(patient.severity),
                            'train/axial_t2': _float_feature(image_array.ravel()),
                            'data/index': _int64_feature(patient.index)}
                example = tf.train.Example(features=tf.train.Features(feature=feature))
                writer.write(example.SerializeToString())
            except Exception as e:
                print('Error generating record')
                print(e)
            print(f'{round(100 * i / len(patients), 3)}% \r', end='')
        writer.close()

    def generate_cross_folds(self, k, patients):
        random.shuffle(patients)

        self.write_log(f'Volume size: {sitk.GetArrayFromImage(patients[0].axial_image).shape}')

        y = [patient.group for patient in patients]
        skf = StratifiedKFold(n_splits=k)
        for i, (train, test) in enumerate(skf.split(patients, y)):
            patients_train = get(patients, train)
            print('Creating train data...')
            self._generate_tfrecords(patients_train, set='train', fold=f'fold{i}')

            patients_test = get(patients, test)
            print('Creating test data...')
            self._generate_tfrecords(patients_test, set='test', fold=f'fold{i}')

    def generate_train_test(self, test_proportion, patients):
        train_path = os.path.join(self.out_path, tfrecord_name('train', self.suffix))
        test_path = os.path.join(self.out_path, tfrecord_name('test', self.suffix))
        if os.path.isfile(train_path) or os.path.isfile(test_path):
            print(f'Train or test with suffix {self.suffix} already exists.')
            print('Press Enter to continue and overwrite.')
            input()

        y = [patient.group for patient in patients]
        patients_train, patients_test, _, _ = train_test_split(patients, y, test_size=test_proportion, stratify=y, random_state=0)

        print('Creating train data...')
        self._generate_tfrecords(patients_train, set='train')

        print('Creating test data...')
        self._generate_tfrecords(patients_test, set='test')
