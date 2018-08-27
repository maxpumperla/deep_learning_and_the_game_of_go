import numpy as np

from dlgo.goboard_fast import Move
from dlgo.gotypes import Player, Point


class ZeroEncoder:
    def __init__(self, board_size):
        self.board_size = board_size
        # 0 - 3. our stones with 1, 2, 3, 4+ liberties
        # 4 - 7. opponent stones with 1, 2, 3, 4+ liberties
        # 8. 1 if we get komi
        # 9. 1 if opponent gets komi
        # 10. move would be illegal due to ko
        self.num_planes = 11

    def encode(self, game_state):
        board_tensor = np.zeros(self.shape())
        next_player = game_state.next_player
        if game_state.next_player == Player.white:
            board_tensor[8] = 1
        else:
            board_tensor[9] = 1
        for r in range(self.board_size):
            for c in range(self.board_size):
                p = Point(row=r + 1, col=c + 1)
                go_string = game_state.board.get_go_string(p)

                if go_string is None:
                    if game_state.does_move_violate_ko(next_player,
                                                       Move.play(p)):
                        board_tensor[10][r][c] = 1
                else:
                    liberty_plane = min(4, go_string.num_liberties) - 1
                    if go_string.color != next_player:
                        liberty_plane += 4
                    board_tensor[liberty_plane][r][c] = 1

        return board_tensor

# tag::encode_move[]
    def encode_move(self, move):
        if move.is_play:
            return (self.board_size * (move.point.row - 1) +   # <1>
                (move.point.col - 1))                          # <1>
        elif move.is_pass:
            return self.board_size * self.board_size           # <2>
        raise ValueError('Cannot encode resign move')          # <3>

    def decode_move_index(self, index):
        if index == self.board_size * self.board_size:
            return Move.pass_turn()
        row = index // self.board_size
        col = index % self.board_size
        return Move.play(Point(row=row + 1, col=col + 1))

    def num_moves(self):
        return self.board_size * self.board_size + 1
# end::encode_move[]

    def shape(self):
        return self.num_planes, self.board_size, self.board_size
