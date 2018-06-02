# This scripts demonstrates all the steps to create and train an
# AGZ-style bot.
# For practical purposes, you would separate this script into multiple
# parts (for initializing, generating self-play games, and training).
# You'll also need to run for many more rounds.

import argparse

import h5py

from keras.layers import Activation, BatchNormalization, Conv2D, Dense, Flatten, Input
from keras.models import Model
from dlgo import scoring
from dlgo import zero
from dlgo.goboard_fast import GameState, Player, Point


def simulate_game(
        board_size,
        black_agent, black_collector,
        white_agent, white_collector):
    print('Starting the game!')
    game = GameState.new_game(board_size)
    agents = {
        Player.black: black_agent,
        Player.white: white_agent,
    }

    black_collector.begin_episode()
    white_collector.begin_episode()
    while not game.is_over():
        next_move = agents[game.next_player].select_move(game)
        game = game.apply_move(next_move)

    game_result = scoring.compute_game_result(game)
    print(game_result)
    # Give the reward to the right agent.
    if game_result.winner == Player.black:
        black_collector.complete_episode(1)
        white_collector.complete_episode(-1)
    else:
        black_collector.complete_episode(-1)
        white_collector.complete_episode(1)


def main():
    # Initialize a zero agent
    board_size = 9
    encoder = zero.ZeroEncoder(board_size)

    board_input = Input(shape=encoder.shape(), name='board_input')

    pb = board_input

    # 4 conv layers with batch normalization
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

    # Create two agents from the model and encoder.
    # 10 is a very small value for rounds_per_move. To train a strong
    # bot, you should run at least a few hundred rounds per move.
    black_agent = zero.ZeroAgent(model, encoder, rounds_per_move=10, c=2.0)
    white_agent = zero.ZeroAgent(model, encoder, rounds_per_move=10, c=2.0)
    c1 = zero.ZeroExperienceCollector()
    c2 = zero.ZeroExperienceCollector()
    black_agent.set_collector(c1)
    white_agent.set_collector(c2)

    # In real training, you should simulate thousands of games for each
    # training batch.
    for i in range(5):
        simulate_game(board_size, black_agent, c1, white_agent, c2)

    exp = zero.combine_experience([c1, c2])
    black_agent.train(exp, 0.01, 2048)


if __name__ == '__main__':
    main()
