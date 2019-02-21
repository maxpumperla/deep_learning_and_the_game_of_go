# tag::encoding[]
import six.moves.cPickle as pickle
import gzip
import numpy as np


def encode_label(j):  # <1>
    e = np.zeros((10, 1))
    e[j] = 1.0
    return e

# <1> We one-hot encode indices to vectors of length 10.
# end::encoding[]


# tag::shape_load[]
def shape_data(data):
    features = [np.reshape(x, (784, 1)) for x in data[0]]  # <1>

    labels = [encode_label(y) for y in data[1]]  # <2>

    return list(zip(features, labels))  # <3>


def load_data_impl():
    # file retrieved by:
    #   wget https://s3.amazonaws.com/img-datasets/mnist.npz -O code/dlgo/nn/mnist.npz
    # code based on:
    #   site-packages/keras/datasets/mnist.py
    path = 'mnist.npz'
    f = np.load(path)
    x_train, y_train = f['x_train'], f['y_train']
    x_test, y_test = f['x_test'], f['y_test']
    f.close()
    return (x_train, y_train), (x_test, y_test)

def load_data():
    train_data, test_data = load_data_impl()
    return shape_data(train_data), shape_data(test_data)


# <1> We flatten the input images to feature vectors of length 784.
# <2> All labels are one-hot encoded.
# <3> Then we create pairs of features and labels.
# <4> Unzipping and loading the MNIST data yields three data sets.
# <5> We discard validation data here and reshape the other two data sets.
# end::shape_load[]
