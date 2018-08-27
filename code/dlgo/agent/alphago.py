# tag::alphago_imports[]
import numpy as np
from dlgo.agent.base import Agent
from dlgo.goboard_fast import Move
from dlgo import kerasutil
import operator
# end::alphago_imports[]


__all__ = [
    'AlphaGoNode',
    'AlphaGoMCTS'
]


# tag::init_alphago_node[]
class AlphaGoNode:
    def __init__(self, parent=None, probability=1.0):
        self.parent = parent  # <1>
        self.children = {}  # <1>

        self.visit_count = 0
        self.q_value = 0
        self.prior_value = probability  # <2>
        self.u_value = probability  # <3>
# <1> Tree nodes have one parent and potentially many children.
# <2> A node is initialized with a prior probability.
# <3> The utility function will be updated during search.
# end::init_alphago_node[]

# tag::select_node[]
    def select_child(self):
        return max(self.children.items(),
                   key=lambda child: child[1].q_value + \
                   child[1].u_value)
# end::select_node[]

# tag::expand_children[]
    def expand_children(self, moves, probabilities):
        for move, prob in zip(moves, probabilities):
            if move not in self.children:
                self.children[move] = AlphaGoNode(probability=prob)
# end::expand_children[]

# tag::update_values[]
    def update_values(self, leaf_value):
        if self.parent is not None:
            self.parent.update_values(leaf_value)  # <1>

        self.visit_count += 1  # <2>

        self.q_value += leaf_value / self.visit_count  # <3>

        if self.parent is not None:
            c_u = 5
            self.u_value = c_u * np.sqrt(self.parent.visit_count) \
                * self.prior_value / (1 + self.visit_count)  # <4>

# <1> We update parents first to ensure we traverse the tree top to bottom.
# <2> Increment the visit count for this node.
# <3> Add the specified leaf value to the Q-value, normalized by visit count.
# <4> Update utility with current visit counts.
# end::update_values[]


# tag::alphago_mcts_init[]
class AlphaGoMCTS(Agent):
    def __init__(self, policy_agent, fast_policy_agent, value_agent,
                 lambda_value=0.5, num_simulations=1000,
                 depth=50, rollout_limit=100):
        self.policy = policy_agent
        self.rollout_policy = fast_policy_agent
        self.value = value_agent

        self.lambda_value = lambda_value
        self.num_simulations = num_simulations
        self.depth = depth
        self.rollout_limit = rollout_limit
        self.root = AlphaGoNode()
# end::alphago_mcts_init[]

# tag::alphago_mcts_rollout[]
    def select_move(self, game_state):
        for simulation in range(self.num_simulations):  # <1>
            current_state = game_state
            node = self.root
            for depth in range(self.depth):  # <2>
                if not node.children:  # <3>
                    if current_state.is_over():
                        break
                    moves, probabilities = self.policy_probabilities(current_state)  # <4>
                    node.expand_children(moves, probabilities)  # <4>

                move, node = node.select_child()  # <5>
                current_state = current_state.apply_move(move)  # <5>

            value = self.value.predict(current_state)  # <6>
            rollout = self.policy_rollout(current_state)  # <6>

            weighted_value = (1 - self.lambda_value) * value + \
                self.lambda_value * rollout  # <7>

            node.update_values(weighted_value)  # <8>
# <1> From current state play out a number of simulations
# <2> Play moves until the specified depth is reached.
# <3> If the current node doesn't have any children...
# <4> ... expand them with probabilities from the strong policy.
# <5> If there are children, we can select one and play the corresponding move.
# <6> Compute output of value network and a rollout by the fast policy.
# <7> Determine the combined value function.
# <8> Update values for this node in the backup phase
# end::alphago_mcts_rollout[]

# tag::alphago_mcts_selection[]
        move = max(self.root.children, key=lambda move:  # <1>
                   self.root.children.get(move).visit_count)  # <1>

        self.root = AlphaGoNode()
        if move in self.root.children:  # <2>
            self.root = self.root.children[move]
            self.root.parent = None

        return move
# <1> Pick most visited child of the root as next move.
# <2> If the picked move is a child, set new root to this child node.
# end::alphago_mcts_selection[]

# tag::alphago_policy_probs[]
    def policy_probabilities(self, game_state):
        encoder = self.policy._encoder
        outputs = self.policy.predict(game_state)
        legal_moves = game_state.legal_moves()
        if not legal_moves:
            return [], []
        encoded_points = [encoder.encode_point(move.point) for move in legal_moves if move.point]
        legal_outputs = outputs[encoded_points]
        normalized_outputs = legal_outputs / np.sum(legal_outputs)
        return legal_moves, normalized_outputs
# end::alphago_policy_probs[]

# tag::alphago_policy_rollout[]
    def policy_rollout(self, game_state):
        for step in range(self.rollout_limit):
            if game_state.is_over():
                break
            move_probabilities = self.rollout_policy.predict(game_state)
            encoder = self.rollout_policy.encoder
            valid_moves = [m for idx, m in enumerate(move_probabilities) 
                           if Move(encoder.decode_point_index(idx)) in game_state.legal_moves()]
            max_index, max_value = max(enumerate(valid_moves), key=operator.itemgetter(1))
            max_point = encoder.decode_point_index(max_index)
            greedy_move = Move(max_point)
            if greedy_move in game_state.legal_moves():
                game_state = game_state.apply_move(greedy_move)

        next_player = game_state.next_player
        winner = game_state.winner()
        if winner is not None:
            return 1 if winner == next_player else -1
        else:
            return 0
# end::alphago_policy_rollout[]


    def serialize(self, h5file):
        raise IOError("AlphaGoMCTS agent can\'t be serialized" +
                       "consider serializing the three underlying" +
                       "neural networks instad.")
