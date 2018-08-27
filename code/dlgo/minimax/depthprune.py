import random

from dlgo.agent import Agent
from dlgo.scoring import GameResult

__all__ = [
    'DepthPrunedAgent',
]

MAX_SCORE = 999999
MIN_SCORE = -999999


def reverse_game_result(game_result):
    if game_result == GameResult.loss:
        return game_result.win
    if game_result == GameResult.win:
        return game_result.loss
    return GameResult.draw


# tag::depth-prune[]
def best_result(game_state, max_depth, eval_fn):
    if game_state.is_over():                               # <1>
        if game_state.winner() == game_state.next_player:  # <1>
            return MAX_SCORE                               # <1>
        else:                                              # <1>
            return MIN_SCORE                               # <1>

    if max_depth == 0:                                     # <2>
        return eval_fn(game_state)                         # <2>

    best_so_far = MIN_SCORE
    for candidate_move in game_state.legal_moves():        # <3>
        next_state = game_state.apply_move(candidate_move) # <4>
        opponent_best_result = best_result(                # <5>
            next_state, max_depth - 1, eval_fn)            # <5>
        our_result = -1 * opponent_best_result             # <6>
        if our_result > best_so_far:                       # <7>
            best_so_far = our_result                       # <7>

    return best_so_far
# end::depth-prune[]


# tag::depth-prune-agent[]
class DepthPrunedAgent(Agent):
    def __init__(self, max_depth, eval_fn):
        Agent.__init__(self)
        self.max_depth = max_depth
        self.eval_fn = eval_fn

    def select_move(self, game_state):
        best_moves = []
        best_score = None
        # Loop over all legal moves.
        for possible_move in game_state.legal_moves():
            # Calculate the game state if we select this move.
            next_state = game_state.apply_move(possible_move)
            # Since our opponent plays next, figure out their best
            # possible outcome from there.
            opponent_best_outcome = best_result(next_state, self.max_depth, self.eval_fn)
            # Our outcome is the opposite of our opponent's outcome.
            our_best_outcome = -1 * opponent_best_outcome
            if (not best_moves) or our_best_outcome > best_score:
                # This is the best move so far.
                best_moves = [possible_move]
                best_score = our_best_outcome
            elif our_best_outcome == best_score:
                # This is as good as our previous best move.
                best_moves.append(possible_move)
        # For variety, randomly select among all equally good moves.
        return random.choice(best_moves)
# end::depth-prune-agent[]
