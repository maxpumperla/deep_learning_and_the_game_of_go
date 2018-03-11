import argparse
import copy
import enum
import random

import numpy as np
from six.moves import input


class Cell(enum.Enum):
    X = 'X'
    O = 'O'
    EMPTY = ' '


class State(object):
    def __init__(self, cells, next_to_play):
        self._cells = copy.copy(cells)
        self._next_to_play = next_to_play

    @property
    def next_to_play(self):
        return self._next_to_play

    def cell(self, row, col):
        return self._cells.get((row, col), Cell.EMPTY)

    def winner(self):
        # 3 in a row
        for row in (0, 1, 2):
            if self.cell(row, 0) != Cell.EMPTY and \
                    self.cell(row, 0) == self.cell(row, 1) == self.cell(row, 2):
                return self.cell(row, 0)
        # 3 in a col
        for col in (0, 1, 2):
            if self.cell(0, col) != Cell.EMPTY and \
                    self.cell(0, col) == self.cell(1, col) == self.cell(2, col):
                return self.cell(0, col)
        # TL to BR diagonal
        if self.cell(0, 0) != Cell.EMPTY and \
                self.cell(0, 0) == self.cell(1, 1) == self.cell(2, 2):
            return self.cell(0, 0)
        # TR to BL diagonal
        if self.cell(0, 2) != Cell.EMPTY and \
                self.cell(0, 2) == self.cell(1, 1) == self.cell(2, 0):
            return self.cell(0, 2)
        return Cell.EMPTY

    def is_over(self):
        if self.winner() != Cell.EMPTY:
            return True
        return all(self.cell(row, col) != Cell.EMPTY
                   for row in (0, 1, 2)
                   for col in (0, 1, 2))

    def get_actions(self):
        actions = []
        for row in (0, 1, 2):
            for col in (0, 1, 2):
                if self.cell(row, col) == Cell.EMPTY:
                    actions.append((row, col))
        return actions

    def apply_move(self, row, col):
        assert self.cell(row, col) == Cell.EMPTY
        next_cells = copy.copy(self._cells)
        next_cells[row, col] = self.next_to_play
        return State(
            next_cells,
            Cell.O if self.next_to_play == Cell.X else Cell.X)


def state_index(state):
    table = {Cell.X: 0, Cell.O: 1, Cell.EMPTY: 2}
    index = 0 if state.next_to_play == Cell.X else 1
    for row in (0, 1, 2):
        for col in (0, 1, 2):
            index = 3 * index + table[state.cell(row, col)]
    return index


def action_index(action):
    row, col = action
    return 3 * row + col


class Q(object):
    def __init__(self):
        self._max_state_index = 3 ** 10
        self._max_action_index = 3 * 3
        self._table = 0.5 + 0.1 * np.random.randn(
            self._max_state_index, self._max_action_index)

    def __call__(self, state, action):
        return self._table[state_index(state), action_index(action)]

    def increment(self, state, action, delta):
        self._table[state_index(state), action_index(action)] += delta

    def load_weights(self, filename):
        self._table = np.load(filename)

    def save_weights(self, filename):
        np.save(filename, self._table)


def new_game():
    return State({}, Cell.X)


def print_game(state):
    rows = 'ABC'
    for row in (0, 1, 2):
        print(rows[row] + '  ' +
              ' | '.join(state.cell(row, col).value for col in (0, 1, 2)))
    print('   1   2   3')
    print('\n')


def select_move(state, q, temperature=0.0):
    actions = state.get_actions()
    if random.random() < temperature:
        # Choose a random action.
        return random.choice(actions)
    # Select the action with the best expected reward.
    ranked_actions = []
    for candidate in actions:
        ranked_actions.append((q(state, candidate), candidate))
    ranked_actions.sort()
    best_q, best_action = ranked_actions[-1]
    return best_action


class Agent(object):
    def __init__(self, q, learning_rate, discount, temperature):
        self._q = q
        self._learning_rate = learning_rate
        self._discount = discount
        self._temperature = temperature
        self._prev_state = None
        self._prev_action = None

    def select_move(self, state):
        if self._prev_state is not None:
            self._learn(state)
        actions = state.get_actions()
        if random.random() < self._temperature:
            # Choose a random action.
            action = random.choice(actions)
        else:
            # Select the action with the best expected reward.
            ranked_actions = []
            for candidate in actions:
                ranked_actions.append((self._q(state, candidate), candidate))
            ranked_actions.sort()
            best_q, action = ranked_actions[-1]
        # Remember the last decision we made for future learning.
        self._prev_state = state
        self._prev_action = action
        return action

    def _learn(self, state):
        # Update the Q function from the new state.
        x_reward = {
            Cell.X: 1,
            Cell.EMPTY: 0,  # draw / game still in progress
            Cell.O: -1,
        }[state.winner()]
        reward = x_reward if self._prev_state.next_to_play == Cell.X \
            else -1 * x_reward
        next_reward = max(self._q(state, next_move)
                          for next_move in state.get_actions())
        delta = reward + self._discount * next_reward - \
            self._q(self._prev_state, self._prev_action)
        self._q.increment(self._prev_state, self._prev_action,
                          self._learning_rate * delta)

    def complete_episode(self, reward):
        delta = reward - self._q(self._prev_state, self._prev_action)
        self._q.increment(self._prev_state, self._prev_action,
                          self._learning_rate * delta)
        self._prev_state = None
        self._prev_action = None


def self_play(q, learning_rate, temperature):
    player_x = Agent(
        q,
        learning_rate=learning_rate,
        discount=1.0,
        temperature=temperature)
    player_o = Agent(
        q,
        learning_rate=learning_rate,
        discount=1.0,
        temperature=temperature)
    game_state = new_game()
    while not game_state.is_over():
        if game_state.next_to_play == Cell.X:
            move = player_x.select_move(game_state)
        else:
            move = player_o.select_move(game_state)
        game_state = game_state.apply_move(*move)
        print_game(game_state)
    winner = game_state.winner()
    x_reward = {
        Cell.X: 1.0,  # X wins
        Cell.EMPTY: 0.0,
        Cell.O: -1.0,  # Y wins
    }[winner]
    player_x.complete_episode(reward=x_reward)
    player_o.complete_episode(reward=-1 * x_reward)
    if winner == Cell.EMPTY:
        print("It's a draw")
    else:
        print("%s wins!" % winner.value)


def human_play(q):
    computer_player = Agent(
        q,
        learning_rate=0.0,
        discount=1.0,
        temperature=0.0)
    human = random.choice([Cell.X, Cell.O])
    game_state = new_game()
    print_game(game_state)
    while not game_state.is_over():
        if game_state.next_to_play == human:
            human_move_txt = input('Your move? ')
            row = 'ABC'.index(human_move_txt[0])
            col = int(human_move_txt[1]) - 1
            move = (row, col)
        else:
            move = computer_player.select_move(game_state)
        game_state = game_state.apply_move(*move)
        print_game(game_state)
    winner = game_state.winner()
    if winner == Cell.EMPTY:
        print("It's a draw")
    else:
        print("%s wins!" % winner.value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', '-t', type=int,
                        help='Number rounds of self-play.')
    parser.add_argument('--input_file', '-i',
                        help='File containing initial Q matrix. If unset, '
                             'will initialize with random weights.')
    parser.add_argument('--output_file', '-o',
                        help='File to save updated Q matrix.')
    args = parser.parse_args()

    q = Q()
    if args.input_file:
        q.load_weights(args.input_file)

    if args.train:
        temperature = 0.2
        learning_rate = 0.75
        for i in range(args.train):
            print("*****************")
            print("Self-play game %d" % i)
            self_play(q, learning_rate=learning_rate, temperature=temperature)
            temperature *= 0.9999
    else:
        human_play(q)

    if args.output_file:
        print("Saving weights to %s" % args.output_file)
        q.save_weights(args.output_file)


if __name__ == '__main__':
    main()
