import unittest

import six

from dlgo.goboard import Board, GameState, Move
from dlgo.gotypes import Player, Point


class BoardTest(unittest.TestCase):
    def test_capture(self):
        board = Board(19, 19)
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.white, Point(1, 2))
        self.assertEqual(Player.black, board.get(Point(2, 2)))
        board.place_stone(Player.white, Point(2, 1))
        self.assertEqual(Player.black, board.get(Point(2, 2)))
        board.place_stone(Player.white, Point(2, 3))
        self.assertEqual(Player.black, board.get(Point(2, 2)))
        board.place_stone(Player.white, Point(3, 2))
        self.assertIsNone(board.get(Point(2, 2)))

    def test_capture_two_stones(self):
        board = Board(19, 19)
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.black, Point(2, 3))
        board.place_stone(Player.white, Point(1, 2))
        board.place_stone(Player.white, Point(1, 3))
        self.assertEqual(Player.black, board.get(Point(2, 2)))
        self.assertEqual(Player.black, board.get(Point(2, 3)))
        board.place_stone(Player.white, Point(3, 2))
        board.place_stone(Player.white, Point(3, 3))
        self.assertEqual(Player.black, board.get(Point(2, 2)))
        self.assertEqual(Player.black, board.get(Point(2, 3)))
        board.place_stone(Player.white, Point(2, 1))
        board.place_stone(Player.white, Point(2, 4))
        self.assertIsNone(board.get(Point(2, 2)))
        self.assertIsNone(board.get(Point(2, 3)))

    def test_capture_is_not_suicide(self):
        board = Board(19, 19)
        board.place_stone(Player.black, Point(1, 1))
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.black, Point(1, 3))
        board.place_stone(Player.white, Point(2, 1))
        board.place_stone(Player.white, Point(1, 2))
        self.assertIsNone(board.get(Point(1, 1)))
        self.assertEqual(Player.white, board.get(Point(2, 1)))
        self.assertEqual(Player.white, board.get(Point(1, 2)))

    def test_remove_liberties(self):
        board = Board(5, 5)
        board.place_stone(Player.black, Point(3, 3))
        board.place_stone(Player.white, Point(2, 2))
        white_string = board.get_go_string(Point(2, 2))
        six.assertCountEqual(
            self,
            [Point(2, 3), Point(2, 1), Point(1, 2), Point(3, 2)],
            white_string.liberties)
        board.place_stone(Player.black, Point(3, 2))
        white_string = board.get_go_string(Point(2, 2))
        six.assertCountEqual(
            self,
            [Point(2, 3), Point(2, 1), Point(1, 2)],
            white_string.liberties)

    def test_empty_triangle(self):
        board = Board(5, 5)
        board.place_stone(Player.black, Point(1, 1))
        board.place_stone(Player.black, Point(1, 2))
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.white, Point(2, 1))

        black_string = board.get_go_string(Point(1, 1))
        six.assertCountEqual(
            self,
            [Point(3, 2), Point(2, 3), Point(1, 3)],
            black_string.liberties)

    def test_GameState_does_move_violate_ko(self):
        # Testing Figures 3.5-3.7.
        game = GameState.new_game(6)
        board = game.board
        board.place_stone(Player.black, Point(1, 2))
        board.place_stone(Player.black, Point(1, 3))
        board.place_stone(Player.white, Point(1, 4))
        board.place_stone(Player.white, Point(1, 6))
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.white, Point(2, 3))
        board.place_stone(Player.black, Point(2, 4))
        board.place_stone(Player.black, Point(2, 5))
        board.place_stone(Player.white, Point(2, 6))
        board.place_stone(Player.black, Point(3, 2))
        board.place_stone(Player.white, Point(3, 3))
        board.place_stone(Player.white, Point(3, 4))
        board.place_stone(Player.white, Point(3, 5))

        next_player, _ = game.situation
        self.assertTrue(next_player, Player.black)

        move = Move(Point(1, 5), is_pass=False, is_resign=False)
        self.assertFalse(game.does_move_violate_ko(Player.black, move))
        move = move.play(Point(1, 5))
        game = game.apply_move(move)

        next_player, _ = game.situation
        self.assertTrue(next_player, Player.white)

        # Verify white can play at 1,4.
        move = Move(Point(1, 4), is_pass=False, is_resign=False)
        self.assertFalse(game.does_move_violate_ko(Player.white, move))
        move = move.play(Point(1, 4))
        game = game.apply_move(move)

        # Testing a real Ko.  Figure 2.5
        game = GameState.new_game(5)
        board = game.board
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.black, Point(3, 1))
        board.place_stone(Player.white, Point(3, 2))
        board.place_stone(Player.black, Point(3, 3))
        board.place_stone(Player.white, Point(4, 1))
        board.place_stone(Player.white, Point(4, 3))
        board.place_stone(Player.white, Point(5, 2))

        # Have black capture 4,2.
        next_player, _ = game.situation
        self.assertTrue(next_player, Player.black)

        move = Move(Point(4, 2), is_pass=False, is_resign=False)
        self.assertFalse(game.does_move_violate_ko(Player.black, move))
        move = move.play(Point(4, 2))
        game = game.apply_move(move)

        # Have white break Ko rule.
        next_player, _ = game.situation
        self.assertTrue(next_player, Player.white)
        move = Move(Point(3, 2), is_pass=False, is_resign=False)
        move = move.play(Point(3, 2))
        self.assertTrue(game.does_move_violate_ko(Player.white, move))

class GameTest(unittest.TestCase):
    def test_new_game(self):
        start = GameState.new_game(19)
        next_state = start.apply_move(Move.play(Point(16, 16)))

        self.assertEqual(start, next_state.previous_state)
        self.assertEqual(Player.white, next_state.next_player)
        self.assertEqual(Player.black, next_state.board.get(Point(16, 16)))


if __name__ == '__main__':
    unittest.main()
