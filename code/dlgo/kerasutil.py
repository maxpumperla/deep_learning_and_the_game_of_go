from __future__ import absolute_import
import tempfile
import os

import h5py
import keras
from keras.models import load_model, save_model


def save_model_to_hdf5_group(model, f):
    # Use Keras save_model to save the full model (including optimizer
    # state) to a file.
    # Then we can embed the contents of that HDF5 file inside ours.
    tempfd, tempfname = tempfile.mkstemp(prefix='tmp-kerasmodel')
    try:
        os.close(tempfd)
        save_model(model, tempfname)
        serialized_model = h5py.File(tempfname, 'r')
        root_item = serialized_model.get('/')
        serialized_model.copy(root_item, f, 'kerasmodel')
        serialized_model.close()
    finally:
        os.unlink(tempfname)


def load_model_from_hdf5_group(f, custom_objects=None):
    # Extract the model into a temporary file. Then we can use Keras
    # load_model to read it.
    tempfd, tempfname = tempfile.mkstemp(prefix='tmp-kerasmodel')
    try:
        os.close(tempfd)
        serialized_model = h5py.File(tempfname, 'w')
        root_item = f.get('kerasmodel')
        for attr_name, attr_value in root_item.attrs.items():
            serialized_model.attrs[attr_name] = attr_value
        for k in root_item.keys():
            f.copy(root_item.get(k), serialized_model, k)
        serialized_model.close()
        return load_model(tempfname, custom_objects=custom_objects)
    finally:
        os.unlink(tempfname)


def set_gpu_memory_target(frac):
    """Configure Tensorflow to use a fraction of available GPU memory.

    Use this for evaluating models in parallel. By default, Tensorflow
    will try to map all available GPU memory in advance. You can
    configure to use just a fraction so that multiple processes can run
    in parallel. For example, if you want to use 2 works, set the
    memory fraction to 0.5.

    If you are using Python multiprocessing, you must call this function
    from the *worker* process (not from the parent).

    This function does nothing if Keras is using a backend other than
    Tensorflow.
    """
    if keras.backend.backend() != 'tensorflow':
        return
    # Do the import here, not at the top, in case Tensorflow is not
    # installed at all.
    import tensorflow as tf
    from keras.backend.tensorflow_backend import set_session
    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = frac
    set_session(tf.Session(config=config))
