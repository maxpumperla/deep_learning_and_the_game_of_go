import random

import numpy as np
from scipy.optimize import minimize

from dlgo import scoring
from dlgo.goboard import GameState
from dlgo.gotypes import Player

__all__ = [
    'calculate_ratings',
]


def simulate_game(black_player, white_player, board_size):
    moves = []
    game = GameState.new_game(board_size)
    agents = {
        Player.black: black_player,
        Player.white: white_player,
    }
    while not game.is_over():
        next_move = agents[game.next_player].select_move(game)
        moves.append(next_move)
        game = game.apply_move(next_move)

    game_result = scoring.compute_game_result(game)

    return game_result.winner


def nll_results(ratings, winners, losers):
    all_ratings = np.concatenate([np.ones(1), ratings])
    winner_ratings = all_ratings[winners]
    loser_ratings = all_ratings[losers]
    log_p_wins = np.log(winner_ratings / (winner_ratings + loser_ratings))
    log_likelihood = np.sum(log_p_wins)
    return -1 * log_likelihood


def calculate_ratings(agents, num_games, board_size):
    num_agents = len(agents)
    agent_ids = list(range(num_agents))

    winners = np.zeros(num_games, dtype=np.int32)
    losers = np.zeros(num_games, dtype=np.int32)

    for i in range(num_games):
        print("Game %d / %d..." % (i + 1, num_games))
        black_id, white_id = random.sample(agent_ids, 2)
        winner = simulate_game(agents[black_id], agents[white_id], board_size)
        if winner == Player.black:
            winners[i] = black_id
            losers[i] = white_id
        else:
            winners[i] = white_id
            losers[i] = black_id

    guess = np.ones(num_agents - 1)
    bounds = [(1e-8, None) for _ in guess]
    result = minimize(
        nll_results, guess,
        args=(winners, losers),
        bounds=bounds)
    assert result.success

    abstract_ratings = np.concatenate([np.ones(1), result.x])
    elo_ratings = 400.0 * np.log10(abstract_ratings)
    min_rating = np.min(elo_ratings)
    # Scale so that the weakest player has rating 0
    return elo_ratings - min_rating
