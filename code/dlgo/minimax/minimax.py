import enum
import random

from dlgo.agent import Agent

__all__ = [
    'MinimaxAgent',
]


# tag::gameresult-enum[]
class GameResult(enum.Enum):
    loss = 1
    draw = 2
    win = 3
# end::gameresult-enum[]


def reverse_game_result(game_result):
    if game_result == GameResult.loss:
        return game_result.win
    if game_result == GameResult.win:
        return game_result.loss
    return GameResult.draw


# tag::minimax-signature[]
def best_result(game_state):
    """Find the best result that next_player can get from this game
    state.

    Returns:
        GameResult.win if next_player can guarantee a win
        GameResult.draw if next_player can guarantee a draw
        GameResult.loss if, no matter what next_player chooses, the
            opponent can still force a win
    """
# end::minimax-signature[]
# tag::minimax-base-case[]
    if game_state.is_over():
        # Game is already over.
        if game_state.winner() == game_state.next_player:
            # We win!
            return GameResult.win
        elif game_state.winner() is None:
            # A draw.
            return GameResult.draw
        else:
            # Opponent won.
            return GameResult.loss
# end::minimax-base-case[]

# tag::minimax-recursive-case[]
    best_result_so_far = GameResult.loss
    opponent = game_state.next_player.other
    for candidate_move in game_state.legal_moves():
        # See what the board would look like if we play this move.
        next_state = game_state.apply_move(candidate_move)
        # Find out our opponent's best move.
        opponent_best_result = best_result(next_state)
        # Whatever our opponent wants, we want the opposite.
        our_result = reverse_game_result(opponent_best_result)
        # See if this result is better than the best we've seen so far.
        if our_result.value > best_result_so_far.value:
            best_result_so_far = our_result
    return best_result_so_far
# end::minimax-recursive-case[]


# tag::minimax-agent[]
class MinimaxAgent(Agent):
    def select_move(self, game_state):
        winning_moves = []
        draw_moves = []
        losing_moves = []
        # Loop over all legal moves.
        for possible_move in game_state.legal_moves():
            # Calculate the game state if we select this move.
            next_state = game_state.apply_move(possible_move)
            # Since our opponent plays next, figure out their best
            # possible outcome from there.
            opponent_best_outcome = best_result(next_state)
            # Our outcome is the opposite of our opponent's outcome.
            our_best_outcome = reverse_game_result(opponent_best_outcome)
            # Add this move to the appropriate list.
            if our_best_outcome == GameResult.win:
                winning_moves.append(possible_move)
            elif our_best_outcome == GameResult.draw:
                draw_moves.append(possible_move)
            else:
                losing_moves.append(possible_move)
        if winning_moves:
            return random.choice(winning_moves)
        if draw_moves:
            return random.choice(draw_moves)
        return random.choice(losing_moves)
# end::minimax-agent[]
