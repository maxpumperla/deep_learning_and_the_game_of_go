import enum
import random

from ..agent import Agent
from ..gotypes import Player

__all__ = [
    'AlphaBetaAgent',
]

MAX_SCORE = 999999
MIN_SCORE = -999999


# tag::alpha-beta-prune-1[]
def alpha_beta_result(game_state, max_depth, best_black, best_white, eval_fn):
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
        opponent_best_result = alpha_beta_result(
            next_state, max_depth - 1,
            best_black, best_white,
            eval_fn)
        # Whatever our opponent wants, we want the opposite.
        our_result = -1 * opponent_best_result

        # See if this result is better than the best we've seen so far.
        if our_result > best_so_far:
            best_so_far = our_result
# end::alpha-beta-prune-1[]

# tag::alpha-beta-prune-2[]
        if game_state.next_player == Player.white:
            # Update our benchmark for white.
            if best_so_far > best_white:
                best_white = best_so_far
            # We are picking a move for white; it only needs to be
            # strong enough to eliminate black's previous move.
            outcome_for_black = -1 * best_so_far
            if outcome_for_black < best_black:
                # candidate_move is strong enough to eliminate this move
                return best_so_far
# end::alpha-beta-prune-2[]
# tag::alpha-beta-prune-3[]
        elif game_state.next_player == Player.black:
            # Update our benchmark for black.
            if best_so_far > best_black:
                best_black = best_so_far
            # We are picking a move for black; it only needs to be
            # strong enough to eliminate white's previous move.
            outcome_for_white = -1 * best_so_far
            if outcome_for_white < best_white:
                return best_so_far
# end::alpha-beta-prune-3[]
# tag::alpha-beta-prune-4[]

    return best_so_far
# end::alpha-beta-prune-4[]


# tag::alpha-beta-agent[]
class AlphaBetaAgent(Agent):
    def __init__(self, max_depth, eval_fn):
        self.max_depth = max_depth
        self.eval_fn = eval_fn

    def select_move(self, game_state):
        best_moves = []
        best_score = None
        best_black = MIN_SCORE
        best_white = MIN_SCORE
        # Loop over all legal moves.
        for possible_move in game_state.legal_moves():
            # Calculate the game state if we select this move.
            next_state = game_state.apply_move(possible_move)
            # Since our opponent plays next, figure out their best
            # possible outcome from there.
            opponent_best_outcome = alpha_beta_result(
                next_state, self.max_depth,
                best_black, best_white,
                self.eval_fn)
            # Our outcome is the opposite of our opponent's outcome.
            our_best_outcome = -1 * opponent_best_outcome
            if (not best_moves) or our_best_outcome > best_score:
                # This is the best move so far.
                best_moves = [possible_move]
                best_score = our_best_outcome
                if game_state.next_player == Player.black:
                    best_black = best_score
                elif game_state.next_player == Player.white:
                    best_white = best_score
            elif our_best_outcome == best_score:
                # This is as good as our previous best move.
                best_moves.append(possible_move)
        # For variety, randomly select among all equally good moves.
        return random.choice(best_moves)
# end::alpha-beta-agent[]
