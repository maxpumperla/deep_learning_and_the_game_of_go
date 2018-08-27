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

    return zip(features, labels)  # <3>


def load_data():
    with gzip.open('mnist.pkl.gz', 'rb') as f:
        train_data, validation_data, test_data = pickle.load(f)  # <4>

    return shape_data(train_data), shape_data(test_data)  # <5>

# <1> We flatten the input images to feature vectors of length 784.
# <2> All labels are one-hot encoded.
# <3> Then we create pairs of features and labels.
# <4> Unzipping and loading the MNIST data yields three data sets.
# <5> We discard validation data here and reshape the other two data sets.
# end::shape_load[]
