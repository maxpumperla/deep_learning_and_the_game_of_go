import unittest

from dlgo.agent.helpers import is_point_an_eye
from dlgo.goboard_fast import Board, GameState, Move
from dlgo.gotypes import Player, Point
from dlgo.encoders.alphago import AlphaGoEncoder


class AlphaGoEncoderTest(unittest.TestCase):
    def test_encoder(self):
        alphago = AlphaGoEncoder()

        start = GameState.new_game(19)
        next_state = start.apply_move(Move.play(Point(16, 16)))
        alphago.encode(next_state)

        self.assertEquals(alphago.name(), 'alphago')
        self.assertEquals(alphago.board_height, 19)
        self.assertEquals(alphago.board_width, 19)
        self.assertEquals(alphago.num_planes, 49)
        self.assertEquals(alphago.shape(), (49, 19, 19))



if __name__ == '__main__':
    unittest.main()
