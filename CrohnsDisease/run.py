import argparse
import tensorflow as tf

from train import Trainer
from model.resnet import ResNet3D
from train_util import generate_decode_function
from infer import Infer

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '1'

def parseArguments():
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Positional mandatory arguments
    parser.add_argument("crohns_or_polyps", help="Task to run", choices=['Crohns_MRI','Polyps_CT'])
    parser.add_argument("base", help="Path to project base")
    parser.add_argument("train_datapath", help="Path to train TF Record")
    parser.add_argument("test_datapath", help="Path to test TF Record")
    parser.add_argument("-record_shape", help="Dimensions of a single dataset feature")
    parser.add_argument("-feature_shape", help="Desired dimensions of input feature to network")

    # Optional arguments
    parser.add_argument("-f", "--fold", help="Fold id", default='')
    parser.add_argument("-bS", "--batch_size", help="Batch size", type=int, default=64)
    parser.add_argument("-lD", "--logdir", help="Directory to log Tensorboard to", default='logdir')
    parser.add_argument("-nB", "--num_batches", help="Number of total training batches", default=None)
    parser.add_argument("-at", "--attention", help="Inclusion of attention layers in network", default=0)
    parser.add_argument("-mode", "--mode", help="Training or testing mode", default="test")
    parser.add_argument("-mP", "--model_path", help="Path to model save", default="CrohnsDisease/trained_models/crohns_model")
    # parser.add_argument("-ma", "--mixedAttention", help="Inclusion of mixed hard-soft attention loss", default=0)
    # parser.add_argument("-lc", "--localisation", help="Terminal Ileum localisation task", default=0)
    # parser.add_argument("-de", "--deeper", help="Depth of network", default=0)

    # Print version
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    # Parse arguments
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    # Parse the arguments
    args = parseArguments()

    # Raw print arguments
    print("Running with arguments: ")
    for a in args.__dict__:
        print(str(a) + ": " + str(args.__dict__[a]))
    args.attention = int(args.attention)
    # args.localisation = int(args.localisation)
    # args.mixedAttention = int(args.mixedAttention)
    # args.deeper = int(args.deeper)

    args.feature_shape = tuple([int(x) for x in args.feature_shape.split(',')])
    args.record_shape = tuple([int(x) for x in args.record_shape.split(',')])

    task = args.__dict__['crohns_or_polyps']
    # if task == 'Polyps_CT':
    #     decode_record = generate_decode_function(args.record_shape, 'image')
    #     model = VGG
    if task == 'Crohns_MRI':
        decode_record = generate_decode_function(args.record_shape, 'axial_t2')
        model = ResNet3D
    args.__dict__['decode_record'] = decode_record

    if args.mode == 'train':
        trainer = Trainer(args, model)
        trainer.train()
    elif args.mode == 'test':
        infer = Infer(args, model)
        # the following are harded coded examples (change to run inference on other images)
        axial_path = './examples/A1 Axial T2.nii'
        coords = [198, 134, 31]

        infer.infer(axial_path, coords, args.record_shape, args.feature_shape)
