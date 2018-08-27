# tag::dl_agent_imports[]
import numpy as np

from dlgo.agent.base import Agent
from dlgo.agent.helpers import is_point_an_eye
from dlgo import encoders
from dlgo import goboard
from dlgo import kerasutil
# end::dl_agent_imports[]
__all__ = [
    'DeepLearningAgent',
    'load_prediction_agent',
]


# tag::dl_agent_init[]
class DeepLearningAgent(Agent):
    def __init__(self, model, encoder):
        Agent.__init__(self)
        self.model = model
        self.encoder = encoder
# end::dl_agent_init[]

# tag::dl_agent_predict[]
    def predict(self, game_state):
        encoded_state = self.encoder.encode(game_state)
        input_tensor = np.array([encoded_state])
        return self.model.predict(input_tensor)[0]

    def select_move(self, game_state):
        num_moves = self.encoder.board_width * self.encoder.board_height
        move_probs = self.predict(game_state)
# end::dl_agent_predict[]

# tag::dl_agent_probabilities[]
        move_probs = move_probs ** 3  # <1>
        eps = 1e-6
        move_probs = np.clip(move_probs, eps, 1 - eps)  # <2>
        move_probs = move_probs / np.sum(move_probs)  # <3>
# <1> Increase the distance between the move likely and least likely moves.
# <2> Prevent move probs from getting stuck at 0 or 1
# <3> Re-normalize to get another probability distribution.
# end::dl_agent_probabilities[]

# tag::dl_agent_candidates[]
        candidates = np.arange(num_moves)  # <1>
        ranked_moves = np.random.choice(
            candidates, num_moves, replace=False, p=move_probs)  # <2>
        for point_idx in ranked_moves:
            point = self.encoder.decode_point_index(point_idx)
            if game_state.is_valid_move(goboard.Move.play(point)) and \
                    not is_point_an_eye(game_state.board, point, game_state.next_player):  # <3>
                return goboard.Move.play(point)
        return goboard.Move.pass_turn()  # <4>
# <1> Turn the probabilities into a ranked list of moves.
# <2> Sample potential candidates
# <3> Starting from the top, find a valid move that doesn't reduce eye-space.
# <4> If no legal and non-self-destructive moves are left, pass.
# end::dl_agent_candidates[]

# tag::dl_agent_serialize[]
    def serialize(self, h5file):
        h5file.create_group('encoder')
        h5file['encoder'].attrs['name'] = self.encoder.name()
        h5file['encoder'].attrs['board_width'] = self.encoder.board_width
        h5file['encoder'].attrs['board_height'] = self.encoder.board_height
        h5file.create_group('model')
        kerasutil.save_model_to_hdf5_group(self.model, h5file['model'])
# end::dl_agent_serialize[]


# tag::dl_agent_deserialize[]
def load_prediction_agent(h5file):
    model = kerasutil.load_model_from_hdf5_group(h5file['model'])
    encoder_name = h5file['encoder'].attrs['name']
    if not isinstance(encoder_name, str):
        encoder_name = encoder_name.decode('ascii')
    board_width = h5file['encoder'].attrs['board_width']
    board_height = h5file['encoder'].attrs['board_height']
    encoder = encoders.get_encoder_by_name(
        encoder_name, (board_width, board_height))
    return DeepLearningAgent(model, encoder)
# tag::dl_agent_deserialize[]
