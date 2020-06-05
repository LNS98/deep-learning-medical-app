"""
Create a set of serialised tensorflow Saved Model ready for serving from a standard
checkpoint version of the same model.
"""

import os
import tensorflow as tf
from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import signature_constants
from tensorflow.python.saved_model import signature_def_utils
from tensorflow.python.saved_model import tag_constants
from tensorflow.python.saved_model.utils import build_tensor_info

 # if you need to re-produce a serving model from a checkpoint version make sure
 # to cahnge this to the desired folders
trained_checkpoint_prefix = '../CrohnsDisease/trained_models_cpu_10_epochs/crohns_model'
export_dir = './serving_models_cpu/1'

graph = tf.Graph()
with tf.compat.v1.Session(graph=graph) as sess:


    # Restore from checkpoint - Robbie does this in infer.py
    loader = tf.compat.v1.train.import_meta_graph(trained_checkpoint_prefix + '.meta')
    loader.restore(sess, trained_checkpoint_prefix)

    # desired outputs from the computational graph
    input_tensor = sess.graph.get_tensor_by_name('ExpandDims:0')
    output_tensor = sess.graph.get_tensor_by_name('Softmax_1:0')
    feature_maps_tensor = sess.graph.get_tensor_by_name('truediv:0')

    model_input = build_tensor_info(input_tensor)
    model_output = build_tensor_info(output_tensor)
    model_feature_maps = build_tensor_info(feature_maps_tensor)

    # Create a signature definition for tfserving
    signature_definition = signature_def_utils.build_signature_def(
        inputs={"Input": model_input},
        outputs={"Output": model_output, "attention_layer": model_feature_maps},
        method_name=signature_constants.PREDICT_METHOD_NAME)


    # create builder to save as a tf serving model
    builder = saved_model_builder.SavedModelBuilder(export_dir)
    builder.add_meta_graph_and_variables(
        sess, [tag_constants.SERVING],
        signature_def_map={
            signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY:
                signature_definition
        })

    # Save the model
    builder.save()
