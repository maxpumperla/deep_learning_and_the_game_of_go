import argparse

import h5py
from keras.layers import Conv2D, Dense, Flatten, Input
from keras.layers import ZeroPadding2D, concatenate
from keras.models import Model

from dlgo import rl
from dlgo import encoders


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--board-size', type=int, default=19)
    parser.add_argument('output_file')
    args = parser.parse_args()

    encoder = encoders.get_encoder_by_name('simple', args.board_size)

    board_input = Input(shape=encoder.shape(), name='board_input')

    conv1a = ZeroPadding2D((2, 2))(board_input)
    conv1b = Conv2D(64, (5, 5), activation='relu')(conv1a)

    conv2a = ZeroPadding2D((1, 1))(conv1b)
    conv2b = Conv2D(64, (3, 3), activation='relu')(conv2a)

    flat = Flatten()(conv2b)
    processed_board = Dense(512)(flat)

    policy_hidden_layer = Dense(
        512, activation='relu')(processed_board)
    policy_output = Dense(
        encoder.num_points(), activation='softmax')(
        policy_hidden_layer)

    value_hidden_layer = Dense(
        512, activation='relu')(
        processed_board)
    value_output = Dense(1, activation='tanh')(
        value_hidden_layer)

    model = Model(inputs=board_input,
                  outputs=[policy_output, value_output])


    new_agent = rl.ACAgent(model, encoder)
    with h5py.File(args.output_file, 'w') as outf:
        new_agent.serialize(outf)


if __name__ == '__main__':
    main()
