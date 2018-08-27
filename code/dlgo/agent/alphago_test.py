import unittest

from dlgo.data.processor import GoDataProcessor
from dlgo.agent.predict import DeepLearningAgent
from dlgo.networks.alphago import alphago_model
from dlgo.agent.pg import PolicyAgent
from dlgo.agent.predict import load_prediction_agent
from dlgo.encoders.alphago import AlphaGoEncoder
from dlgo.rl.simulate import experience_simulation
from dlgo.networks.alphago import alphago_model
from dlgo.rl import ValueAgent, load_experience
from dlgo.agent import load_prediction_agent, load_policy_agent, AlphaGoMCTS
from dlgo.rl import load_value_agent
from dlgo.goboard_fast import GameState

from keras.callbacks import ModelCheckpoint
import h5py
import numpy as np

class AlphaGoAgentTest(unittest.TestCase):
    def test_1_supervised_learning(self):
        rows, cols = 19, 19
        encoder = AlphaGoEncoder()

        input_shape = (encoder.num_planes, rows, cols)
        alphago_sl_policy = alphago_model(input_shape, is_policy_net=True)

        alphago_sl_policy.compile('sgd', 'categorical_crossentropy', metrics=['accuracy'])

        alphago_sl_agent = DeepLearningAgent(alphago_sl_policy, encoder)

        inputs = np.ones((10,) + input_shape)
        outputs = alphago_sl_policy.predict(inputs)
        assert(outputs.shape == (10, 361))

        with h5py.File('test_alphago_sl_policy.h5', 'w') as sl_agent_out:
            alphago_sl_agent.serialize(sl_agent_out)

    def test_2_reinforcement_learning(self):
        encoder = AlphaGoEncoder()

        sl_agent = load_prediction_agent(h5py.File('test_alphago_sl_policy.h5'))
        sl_opponent = load_prediction_agent(h5py.File('test_alphago_sl_policy.h5'))

        alphago_rl_agent = PolicyAgent(sl_agent.model, encoder)
        opponent = PolicyAgent(sl_opponent.model, encoder)

        num_games = 1
        experience = experience_simulation(num_games, alphago_rl_agent, opponent)

        alphago_rl_agent.train(experience)

        with h5py.File('test_alphago_rl_policy.h5', 'w') as rl_agent_out:
            alphago_rl_agent.serialize(rl_agent_out)

        with h5py.File('test_alphago_rl_experience.h5', 'w') as exp_out:
           experience.serialize(exp_out)        

    def test_3_alphago_value(self):
        rows, cols = 19, 19
        encoder = AlphaGoEncoder()
        input_shape = (encoder.num_planes, rows, cols)
        alphago_value_network = alphago_model(input_shape)

        alphago_value = ValueAgent(alphago_value_network, encoder)

        experience = load_experience(h5py.File('test_alphago_rl_experience.h5', 'r'))

        alphago_value.train(experience)

        with h5py.File('test_alphago_value.h5', 'w') as value_agent_out:
            alphago_value.serialize(value_agent_out)

    def test_4_alphago_mcts(self):
        fast_policy = load_prediction_agent(h5py.File('test_alphago_sl_policy.h5', 'r'))
        strong_policy = load_policy_agent(h5py.File('test_alphago_rl_policy.h5', 'r'))
        value = load_value_agent(h5py.File('test_alphago_value.h5', 'r'))

        alphago = AlphaGoMCTS(strong_policy, fast_policy, value,
                              num_simulations=20, depth=5, rollout_limit=10)
        start = GameState.new_game(19)
        alphago.select_move(start)


if __name__ == '__main__':
    unittest.main()
