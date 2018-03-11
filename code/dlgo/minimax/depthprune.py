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
    """Find the best result that next_player can get from this game
    state.
    """
    if game_state.is_over():
        # Game is already over.
        if game_state.winner() == game_state.next_player:
            return MAX_SCORE
        else:
            return MIN_SCORE

    if max_depth == 0:
        # We have reached our maximum search depth. Use our heuristic to
        # decide how good this sequence is.
        return eval_fn(game_state)

    best_so_far = MIN_SCORE
    # Loop over all valid moves.
    for candidate_move in game_state.legal_moves():
        # See what the board would look like if we play this move.
        next_state = game_state.apply_move(candidate_move)
        # Find out our opponent's best result from that position.
        opponent_best_result = best_result(next_state, max_depth - 1, eval_fn)
        # Whatever our opponent wants, we want the opposite.
        our_result = -1 * opponent_best_result
        # See if this result is better than the best we've seen so far.
        if our_result > best_so_far:
            best_so_far = our_result

    return best_so_far
# end::depth-prune[]


# tag::depth-prune-agent[]
class DepthPrunedAgent(Agent):
    def __init__(self, max_depth, eval_fn):
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
