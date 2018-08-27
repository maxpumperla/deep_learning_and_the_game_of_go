import argparse

import h5py

from keras.layers import Dense, Input
from keras.models import Model
import dlgo.networks
from dlgo import rl
from dlgo import encoders


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--board-size', type=int, default=19)
    parser.add_argument('--network', default='large')
    parser.add_argument('output_file')
    args = parser.parse_args()

    encoder = encoders.get_encoder_by_name('simple', args.board_size)
    board_input = Input(shape=encoder.shape(), name='board_input')
    # action_input = Input(shape=(encoder.num_points(),), name='action_input')

    processed_board = board_input
    network = getattr(dlgo.networks, args.network)
    for layer in network.layers(encoder.shape()):
        processed_board = layer(processed_board)

    value_output = Dense(1, activation='sigmoid')(processed_board)

    model = Model(inputs=board_input, outputs=value_output)

    new_agent = rl.ValueAgent(model, encoder)
    with h5py.File(args.output_file, 'w') as outf:
        new_agent.serialize(outf)


if __name__ == '__main__':
    main()
