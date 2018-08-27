import numpy as np
from keras.optimizers import SGD

from ..agent import Agent

__all__ = [
    'ZeroAgent',
]


# tag::branch_struct[]
class Branch:
    def __init__(self, prior):
        self.prior = prior
        self.visit_count = 0
        self.total_value = 0.0
# end::branch_struct[]


# tag::node_class_defn[]
class ZeroTreeNode:
# end::node_class_defn[]
# tag::node_class_body[]
    def __init__(self, state, value, priors, parent, last_move):
        self.state = state
        self.value = value
        self.parent = parent                      # <1>
        self.last_move = last_move                # <1>
        self.total_visit_count = 1
        self.branches = {}
        for move, p in priors.items():
            if state.is_valid_move(move):
                self.branches[move] = Branch(p)
        self.children = {}                        # <2>

    def moves(self):                              # <3>
        return self.branches.keys()               # <3>

    def add_child(self, move, child_node):        # <4>
        self.children[move] = child_node          # <4>

    def has_child(self, move):                    # <5>
        return move in self.children              # <5>

    def get_child(self, move):                    # <6>
        return self.children[move]                # <6>
# end::node_class_body[]

# tag::node_record_visit[]
    def record_visit(self, move, value):
        self.total_visit_count += 1
        self.branches[move].visit_count += 1
        self.branches[move].total_value += value
# end::node_record_visit[]

# tag::node_class_helpers[]
    def expected_value(self, move):
        branch = self.branches[move]
        if branch.visit_count == 0:
            return 0.0
        return branch.total_value / branch.visit_count

    def prior(self, move):
        return self.branches[move].prior

    def visit_count(self, move):
        if move in self.branches:
            return self.branches[move].visit_count
        return 0
# end::node_class_helpers[]


# tag::zero_defn[]
class ZeroAgent(Agent):
# end::zero_defn[]
    def __init__(self, model, encoder, rounds_per_move=1600, c=2.0):
        self.model = model
        self.encoder = encoder

        self.collector = None

        self.num_rounds = rounds_per_move
        self.c = c

# tag::zero_select_move_defn[]
    def select_move(self, game_state):
# end::zero_select_move_defn[]
# tag::zero_walk_down[]
        root = self.create_node(game_state)           # <1>

        for i in range(self.num_rounds):              # <2>
            node = root
            next_move = self.select_branch(node)
            while node.has_child(next_move):          # <3>
                node = node.get_child(next_move)
                next_move = self.select_branch(node)
# end::zero_walk_down[]

# tag::zero_back_up[]
            new_state = node.state.apply_move(next_move)
            child_node = self.create_node(
                new_state, move=next_move, parent=node)

            move = next_move
            value = -1 * child_node.value             # <1>
            while node is not None:
                node.record_visit(move, value)
                move = node.last_move
                node = node.parent
                value = -1 * value
# end::zero_back_up[]

# tag::zero_record_collector[]
        if self.collector is not None:
            root_state_tensor = self.encoder.encode(game_state)
            visit_counts = np.array([
                root.visit_count(
                    self.encoder.decode_move_index(idx))
                for idx in range(self.encoder.num_moves())
            ])
            self.collector.record_decision(
                root_state_tensor, visit_counts)
# end::zero_record_collector[]

# tag::zero_select_max_visit_count[]
        return max(root.moves(), key=root.visit_count)
# end::zero_select_max_visit_count[]

    def set_collector(self, collector):
        self.collector = collector

# tag::zero_select_branch[]
    def select_branch(self, node):
        total_n = node.total_visit_count

        def score_branch(move):
            q = node.expected_value(move)
            p = node.prior(move)
            n = node.visit_count(move)
            return q + self.c * p * np.sqrt(total_n) / (n + 1)

        return max(node.moves(), key=score_branch)             # <1>
# end::zero_select_branch[]

# tag::zero_create_node[]
    def create_node(self, game_state, move=None, parent=None):
        state_tensor = self.encoder.encode(game_state)
        model_input = np.array([state_tensor])                 # <1>
        priors, values = self.model.predict(model_input)
        priors = priors[0]                                     # <2>
        value = values[0][0]                                   # <2>
        move_priors = {                                        # <3>
            self.encoder.decode_move_index(idx): p             # <3>
            for idx, p in enumerate(priors)                    # <3>
        }                                                      # <3>
        new_node = ZeroTreeNode(
            game_state, value,
            move_priors,
            parent, move)
        if parent is not None:
            parent.add_child(move, new_node)
        return new_node
# end::zero_create_node[]

# tag::zero_train[]
    def train(self, experience, learning_rate, batch_size):     # <1>
        num_examples = experience.states.shape[0]

        model_input = experience.states

        visit_sums = np.sum(                                    # <2>
            experience.visit_counts, axis=1).reshape(           # <2>
            (num_examples, 1))                                  # <2>
        action_target = experience.visit_counts / visit_sums    # <2>

        value_target = experience.rewards

        self.model.compile(
            SGD(lr=learning_rate),
            loss=['categorical_crossentropy', 'mse'])
        self.model.fit(
            model_input, [action_target, value_target],
            batch_size=batch_size)
# end::zero_train[]
