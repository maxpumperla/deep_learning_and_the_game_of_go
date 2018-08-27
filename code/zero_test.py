import argparse

import h5py

from keras.layers import Activation, BatchNormalization, Conv2D, Dense, Flatten, Input
from keras.models import Model
from dlgo import zero
from dlgo.goboard_fast import GameState, Player, Point


def main():
    board_size = 9
    encoder = zero.ZeroEncoder(board_size)

    board_input = Input(shape=encoder.shape(), name='board_input')

    pb = board_input

    for i in range(4):
        pb = Conv2D(64, (3, 3),
            padding='same',
            data_format='channels_first')(pb)
        pb = BatchNormalization(axis=1)(pb)
        pb = Activation('relu')(pb)

    # Policy output
    policy_conv = Conv2D(2, (1, 1), data_format='channels_first')(pb)
    policy_batch = BatchNormalization(axis=1)(policy_conv)
    policy_relu = Activation('relu')(policy_batch)
    policy_flat = Flatten()(policy_relu)
    policy_output = Dense(encoder.num_moves(), activation='softmax')(
        policy_flat)

    # Value output
    value_conv = Conv2D(1, (1, 1), data_format='channels_first')(pb)
    value_batch = BatchNormalization(axis=1)(value_conv)
    value_relu = Activation('relu')(value_batch)
    value_flat = Flatten()(value_relu)
    value_hidden = Dense(256, activation='relu')(value_flat)
    value_output = Dense(1, activation='tanh')(value_hidden)

    model = Model(
        inputs=[board_input],
        outputs=[policy_output, value_output])

    c1 = zero.ZeroExperienceCollector()
    c2 = zero.ZeroExperienceCollector()
    black_agent = zero.ZeroAgent(model, encoder, rounds_per_move=10, c=2.0)
    white_agent = zero.ZeroAgent(model, encoder, rounds_per_move=10, c=2.0)
    black_agent.set_collector(c1)
    white_agent.set_collector(c2)

    print('Starting the game!')
    game = GameState.new_game(board_size)

    c1.begin_episode()
    c2.begin_episode()
    black_move = black_agent.select_move(game)
    print('B', black_move)
    game = game.apply_move(black_move)
    white_move = white_agent.select_move(game)
    print('W', white_move)
    black_move = black_agent.select_move(game)
    print('B', black_move)

    c1.complete_episode(1)
    c2.complete_episode(-1)
    exp = zero.combine_experience([c1, c2])
    black_agent.train(exp, 0.01, 2048)


if __name__ == '__main__':
    main()
