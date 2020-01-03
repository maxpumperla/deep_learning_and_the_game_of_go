import chess as _chess
from dlgo.gotypes import Player

__all__ = [
    'GameState',
]

class GameState:
    def __init__(self, board):
        self.board = board
        self.next_player = Player.white if board.turn else Player.black

    def apply_move(self, move):
        """Return the new GameState after applying the move."""
        next_board = self.board.copy()
        next_board.push(move)
        return GameState(next_board)

    @classmethod
    def new_game(cls):
        board = _chess.Board()
        return GameState(board)

    def is_valid_move(self, move):
        return (move in self.board.legal_moves)

    def legal_moves(self):
        return list(self.board.legal_moves)

    def is_over(self):
        return self.board.is_game_over()

    def winner(self):
        if self.board.is_checkmate():
            return Player.black if self.board.turn else Player.white
        return None
