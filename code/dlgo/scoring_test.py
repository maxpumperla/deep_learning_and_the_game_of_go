import unittest

from dlgo import scoring
from dlgo.goboard import Board
from dlgo.gotypes import Player, Point


class ScoringTest(unittest.TestCase):
    def test_scoring(self):
        # .w.ww
        # wwww.
        # bbbww
        # .bbbb
        # .b.b.
        board = Board(5, 5)
        board.place_stone(Player.black, Point(1, 2))
        board.place_stone(Player.black, Point(1, 4))
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.black, Point(2, 3))
        board.place_stone(Player.black, Point(2, 4))
        board.place_stone(Player.black, Point(2, 5))
        board.place_stone(Player.black, Point(3, 1))
        board.place_stone(Player.black, Point(3, 2))
        board.place_stone(Player.black, Point(3, 3))
        board.place_stone(Player.white, Point(3, 4))
        board.place_stone(Player.white, Point(3, 5))
        board.place_stone(Player.white, Point(4, 1))
        board.place_stone(Player.white, Point(4, 2))
        board.place_stone(Player.white, Point(4, 3))
        board.place_stone(Player.white, Point(4, 4))
        board.place_stone(Player.white, Point(5, 2))
        board.place_stone(Player.white, Point(5, 4))
        board.place_stone(Player.white, Point(5, 5))
        territory = scoring.evaluate_territory(board)
        self.assertEqual(9, territory.num_black_stones)
        self.assertEqual(4, territory.num_black_territory)
        self.assertEqual(9, territory.num_white_stones)
        self.assertEqual(3, territory.num_white_territory)
        self.assertEqual(0, territory.num_dame)
