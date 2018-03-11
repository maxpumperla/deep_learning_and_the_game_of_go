import enum
import random

import keras.backend as K
import numpy as np
from keras.layers import Dense
from keras.models import Sequential


class Move(enum.Enum):
    PASS = 0
    FORFEIT = 1


class ReferenceAgent(object):
    """Agent that never learns."""
    def select_move(self):
        return random.choice([Move.PASS, Move.FORFEIT])


class LearningAgent(object):
    def __init__(self):
        self._learning_rate = 0.05
        self._model = Sequential()
        self._model.add(Dense(2, input_dim=1, activation='softmax'))
        self._states = []
        self._actions = []

    def begin_episode(self):
        self._states = []
        self._actions = []

    def select_move(self):
        self._states.append(K.ones((1, 1)))
        p = self._model.predict(np.ones(1))[0]
        action = np.random.choice(2, p=p)
        assert action in (0, 1)
        self._actions.append(action)
        if action == 0:
            return Move.PASS
        return Move.FORFEIT

    def learn(self, reward):
        for s, a in zip(self._states, self._actions):
            policy = self._model(s)
            log_policy = K.log(policy)
            chosen_p = K.gather(
                K.gather(log_policy, K.constant(0, dtype='int32')),
                K.constant(a, dtype='int32'))
            gradients = K.gradients(chosen_p, self._model.trainable_weights)
            lr = K.constant(self._learning_rate)
            r = K.constant(reward)
            deltas = K.batch_get_value(
                [lr * gradient * r for gradient in gradients])
            weights = self._model.get_weights()
            updated_weights = [weight + delta
                               for weight, delta in zip(weights, deltas)]
            self._model.set_weights(updated_weights)


def simulate_game(agent1, agent2):
    """Returns 1 if agent1 wins, -1 if agent2 wins, 0 for draw."""
    agent1_moves = []
    agent2_moves = []
    for _ in range(3):
        agent1_moves.append(agent1.select_move())
        agent2_moves.append(agent2.select_move())
    agent1_score = sum(1 for move in agent1_moves if move == Move.FORFEIT)
    agent2_score = sum(1 for move in agent2_moves if move == Move.FORFEIT)
    if agent1_score < agent2_score:
        return 1
    elif agent1_score > agent2_score:
        return -1
    return 0


def train():
    rl_agent = LearningAgent()
    ref_agent = ReferenceAgent()
    results = []
    for i in range(10000):
        rl_agent.begin_episode()
        result = simulate_game(rl_agent, ref_agent)
        rl_agent.learn(result)
        results.append(result)
        print("Score %d/10" % sum(results[-10:]))


def main():
    train()


if __name__ == '__main__':
    main()
