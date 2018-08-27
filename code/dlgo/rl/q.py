import numpy as np

from keras.optimizers import SGD

from dlgo import encoders
from dlgo import goboard
from dlgo import kerasutil
from dlgo.agent import Agent
from dlgo.agent.helpers import is_point_an_eye

__all__ = [
    'QAgent',
    'load_q_agent',
]


class QAgent(Agent):
    def __init__(self, model, encoder, policy='eps-greedy'):
        Agent.__init__(self)
        self.model = model
        self.encoder = encoder
        self.collector = None
        self.temperature = 0.0
        self.policy = policy

        self.last_move_value = 0

    def set_temperature(self, temperature):
        self.temperature = temperature

    def set_collector(self, collector):
        self.collector = collector

    def set_policy(self, policy):
        if policy not in ('eps-greedy', 'weighted'):
            raise ValueError(policy)
        self.policy = policy

    def select_move(self, game_state):
        board_tensor = self.encoder.encode(game_state)

        # Loop over all legal moves.
        moves = []
        board_tensors = []
        for move in game_state.legal_moves():
            if not move.is_play:
                continue
            moves.append(self.encoder.encode_point(move.point))
            board_tensors.append(board_tensor)
        if not moves:
            return goboard.Move.pass_turn()

        num_moves = len(moves)
        board_tensors = np.array(board_tensors)
        move_vectors = np.zeros((num_moves, self.encoder.num_points()))
        for i, move in enumerate(moves):
            move_vectors[i][move] = 1

        values = self.model.predict([board_tensors, move_vectors])
        values = values.reshape(len(moves))

        if self.policy == 'eps-greedy':
            ranked_moves = self.rank_moves_eps_greedy(values)
        elif self.policy == 'weighted':
            ranked_moves = self.rank_moves_weighted(values)
        else:
            ranked_moves = None

        for move_idx in ranked_moves:
            point = self.encoder.decode_point_index(moves[move_idx])
            if not is_point_an_eye(game_state.board,
                                   point,
                                   game_state.next_player):
                if self.collector is not None:
                    self.collector.record_decision(
                        state=board_tensor,
                        action=moves[move_idx],
                    )
                self.last_move_value = float(values[move_idx])
                return goboard.Move.play(point)
        # No legal, non-self-destructive moves less.
        return goboard.Move.pass_turn()

    def rank_moves_eps_greedy(self, values):
        if np.random.random() < self.temperature:
            values = np.random.random(values.shape)
        # This ranks the moves from worst to best.
        ranked_moves = np.argsort(values)
        # Return them in best-to-worst order.
        return ranked_moves[::-1]

    def rank_moves_weighted(self, values):
        p = values / np.sum(values)
        p = np.power(p, 1.0 / self.temperature)
        p = p / np.sum(p)
        return np.random.choice(
            np.arange(0, len(values)),
            size=len(values),
            p=p,
            replace=False)

    def train(self, experience, lr=0.1, batch_size=128):
        opt = SGD(lr=lr)
        self.model.compile(loss='mse', optimizer=opt)

        n = experience.states.shape[0]
        num_moves = self.encoder.num_points()
        y = np.zeros((n,))
        actions = np.zeros((n, num_moves))
        for i in range(n):
            action = experience.actions[i]
            reward = experience.rewards[i]
            actions[i][action] = 1
            y[i] = 1 if reward > 0 else 0

        self.model.fit(
            [experience.states, actions], y,
            batch_size=batch_size,
            epochs=1)

    def serialize(self, h5file):
        h5file.create_group('encoder')
        h5file['encoder'].attrs['name'] = self.encoder.name()
        h5file['encoder'].attrs['board_width'] = self.encoder.board_width
        h5file['encoder'].attrs['board_height'] = self.encoder.board_height
        h5file.create_group('model')
        kerasutil.save_model_to_hdf5_group(self.model, h5file['model'])

    def diagnostics(self):
        return {'value': self.last_move_value}


def load_q_agent(h5file):
    model = kerasutil.load_model_from_hdf5_group(h5file['model'])
    encoder_name = h5file['encoder'].attrs['name']
    if not isinstance(encoder_name, str):
        encoder_name = encoder_name.decode('ascii')
    board_width = h5file['encoder'].attrs['board_width']
    board_height = h5file['encoder'].attrs['board_height']
    encoder = encoders.get_encoder_by_name(
        encoder_name,
        (board_width, board_height))
    return QAgent(model, encoder)
