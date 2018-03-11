from __future__ import absolute_import
from keras.layers.core import Dense, Activation, Flatten
from keras.layers.convolutional import Conv2D, ZeroPadding2D


def layers(input_shape):
    return [
        Dense(128, input_shape=input_shape),
        Activation('relu'),
        Dense(128, input_shape=input_shape),
        Activation('relu'),
        Flatten(),
        Dense(128),
        Activation('relu'),
    ]
