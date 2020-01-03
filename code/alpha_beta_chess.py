from six.moves import input

import chess as _chess
from dlgo import chess
from dlgo.gotypes import Player
from dlgo import minimax

piece_values = {_chess.KING: 0,
                _chess.PAWN: 1,
                _chess.BISHOP: 3,
                _chess.KNIGHT: 3,
                _chess.ROOK: 5,
                _chess.QUEEN: 9}

def static_evaluation(game):
    board = game.board
    score = 0
    for piece in board.piece_map().values():
        value = piece_values[piece.piece_type]
        factor = 1 if piece.color == board.turn else -1
        score += factor * value
    score -= 100 if board.is_checkmate() else 0
    return score

def move_from_uci(game, uci):
    try:
        move = _chess.Move.from_uci(uci)
    except ValueError:
        print('expected an UCI move')
        return None
    if not game.is_valid_move(move):
        print('expected a valid move')
        return None
    return move

def main():
    game = chess.GameState.new_game()
    bot = minimax.AlphaBetaAgent(3, static_evaluation)

    while not game.is_over():
        print(game.board)
        if game.next_player == Player.white:
            human_move = input('-- ')
            move = move_from_uci(game, human_move.strip())
            if move is None:
                print('try again, e.g., %s' % game.legal_moves()[0].uci())
                continue
        else:
            move = bot.select_move(game)
        print(move)
        game = game.apply_move(move)


if __name__ == '__main__':
    main()
