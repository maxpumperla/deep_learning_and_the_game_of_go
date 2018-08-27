# tag::termination_imports[]
from dlgo import goboard
from dlgo.agent.base import Agent
from dlgo import scoring
# end::termination_imports[]


# tag::termination_strategy[]
class TerminationStrategy:

    def __init__(self):
        pass

    def should_pass(self, game_state):
        return False

    def should_resign(self, game_state):
        return False
# end::termination_strategy[]


# tag::opponent_passes[]
class PassWhenOpponentPasses(TerminationStrategy):

    def should_pass(self, game_state):
        if game_state.last_move is not None:
            return True if game_state.last_move.is_pass else False
# end::opponent_passes[]


# tag::resign_margin[]
class ResignLargeMargin(TerminationStrategy):

    def __init__(self, own_color, cut_off_move, margin):
        TerminationStrategy.__init__(self)
        self.own_color = own_color
        self.cut_off_move = cut_off_move
        self.margin = margin

        self.moves_played = 0

    def should_pass(self, game_state):
        return False

    def should_resign(self, game_state):
        self.moves_played += 1
        if self.moves_played:
            game_result = scoring.compute_game_result(self)
            if game_result.winner != self.own_color and game_result.winning_margin >= self.margin:
                return True
        return False
# end::resign_margin[]


# tag::termination_agent[]
class TerminationAgent(Agent):

    def __init__(self, agent, strategy=None):
        Agent.__init__(self)
        self.agent = agent
        self.strategy = strategy if strategy is not None \
            else TerminationStrategy()

    def select_move(self, game_state):
        if self.strategy.should_pass(game_state):
            return goboard.Move.pass_turn()
        elif self.strategy.should_resign(game_state):
            return goboard.Move.resign()
        else:
            return self.agent.select_move(game_state)
# end::termination_agent[]


# tag::get_termination[]
def get(termination):
    if termination == 'opponent_passes':
        return PassWhenOpponentPasses()
    else:
        raise ValueError("Unsupported termination strategy: {}"
                         .format(termination))
# end::get_termination[]
