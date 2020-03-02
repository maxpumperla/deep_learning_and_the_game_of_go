from keras.layers.core import Activation, Dense, Dropout, Flatten
from keras.layers.convolutional import Conv2D, ZeroPadding2D
from keras.layers.pooling import MaxPooling2D

def layers(input_shape):
    return [
        ZeroPadding2D(padding=1, data_format="channels_first", input_shape=input_shape),
        Conv2D(48, (3, 3), data_format="channels_first"),
        Activation("relu"),

        Conv2D(48, (5, 5), data_format="channels_first"),
        Activation("relu"),

        Conv2D(48, (5, 5), data_format="channels_first"),
        Activation("relu"),

        Conv2D(64, (7, 7), data_format="channels_first"),
        Activation("relu"),
        Dropout(0.1),

        MaxPooling2D((3, 3), strides=(1,1), data_format="channels_first"),
        Dropout(0.3),
        Flatten(),

        Dense(512),
        Activation("relu"),
        Dropout(0.5)
    ]