import argparse

import h5py

from keras.layers import Activation, Dense
from keras.models import Sequential
from keras.optimizers import SGD
import dlgo.networks.leaky
from dlgo import agent
from dlgo import encoders


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--board-size', type=int, default=19)
    parser.add_argument('output_file')
    args = parser.parse_args()
    board_size = args.board_size
    output_file = args.output_file

    encoder = encoders.simple.SimpleEncoder((board_size, board_size))
    model = Sequential()
    for layer in dlgo.networks.large.layers(encoder.shape()):
        model.add(layer)
    model.add(Dense(encoder.num_points()))
    model.add(Activation('softmax'))
    new_agent = agent.PolicyAgent(model, encoder)

    with h5py.File(output_file, 'w') as outf:
        new_agent.serialize(outf)


if __name__ == '__main__':
    main()
