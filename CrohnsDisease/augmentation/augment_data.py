from dltk.io.augmentation import *
from dltk.io.preprocessing import *
import numpy as np
import cv2
import scipy
import random
import math
import multiprocessing as mp
from multiprocessing import Pool
import functools
import random

# Parameters
angle_std = 4
alpha, sigma = 6e3, 50

def crop(image, desired_size, mode='center'):
    diff = image.shape - np.array(desired_size)
    if mode == 'random':
        ds = [random.randint(0, d) for d in diff]
    elif mode == 'center':
        ds = [int(round(d / 2)) for d in diff]

    res = [diff_i - ds_i for diff_i, ds_i in zip(diff, ds)]
    res = [-r if r != 0 else None for r in res]
    return image[ds[0]:res[0], ds[1]:res[1], ds[2]:res[2]]

def random_rotate(image):
    angle = np.random.normal(loc=0, scale=angle_std)
    return scipy.ndimage.rotate(image, angle, axes=(1, 2), reshape=False, order=5, mode='nearest')

def augment(image, out_dims=None):
    # Initial crop to remove border artefacts
    image = crop(image, (image.shape[0] - 4, image.shape[1] - 8, image.shape[2] - 8), mode='center')

    image = random_rotate(image)
    image = flip(image, axis=2)
    image = crop(image, out_dims, mode='random')
    image = add_gaussian_noise(image, sigma=0.005)
    # image = elastic_transform(image, alpha=[1, alpha, alpha],
    #                                      sigma=[1 ,sigma, sigma])
    image = whitening(image)
    return image

# Process results in the same output shape as augment, and the same standardisation
def process(image, out_dims=None):
    image = crop(image, out_dims, mode='center')
    image = whitening(image)
    return image

class Augmentor:
    def __init__(self, out_dims):
        self.mappable_augment = functools.partial(augment, out_dims=out_dims)
        self.mappable_process = functools.partial(process, out_dims=out_dims)

    def __call__(self, image):
        return augment(image, self.out_dims)

    def paralellise_f(self, images, f):
        with Pool(processes=mp.cpu_count()) as pool:
            print(f'Processing {len(images)} images \r', end='')
            return pool.map(f, images)

    def augment_batch(self, images):
        return self.paralellise_f(images, self.mappable_augment)

    def process_test_set(self, images):
        return self.paralellise_f(images, self.mappable_process)
