import unittest

from dlgo.agent.helpers import is_point_an_eye
from dlgo.goboard import Board
from dlgo.gotypes import Player, Point


class EyeTest(unittest.TestCase):
    def test_corner(self):
        board = Board(19, 19)
        board.place_stone(Player.black, Point(1, 2))
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.black, Point(2, 1))
        self.assertTrue(is_point_an_eye(board, Point(1, 1), Player.black))
        self.assertFalse(is_point_an_eye(board, Point(1, 1), Player.white))

    def test_corner_false_eye(self):
        board = Board(19, 19)
        board.place_stone(Player.black, Point(1, 2))
        board.place_stone(Player.black, Point(2, 1))
        self.assertFalse(is_point_an_eye(board, Point(1, 1), Player.black))
        board.place_stone(Player.white, Point(2, 2))
        self.assertFalse(is_point_an_eye(board, Point(1, 1), Player.black))

    def test_middle(self):
        board = Board(19, 19)
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.black, Point(3, 2))
        board.place_stone(Player.black, Point(4, 2))
        board.place_stone(Player.black, Point(4, 3))
        board.place_stone(Player.white, Point(4, 4))
        board.place_stone(Player.black, Point(3, 4))
        board.place_stone(Player.black, Point(2, 4))
        board.place_stone(Player.black, Point(2, 3))
        self.assertTrue(is_point_an_eye(board, Point(3, 3), Player.black))


if __name__ == '__main__':
    unittest.main()
