# tag::bot_vs_bot[]
from dlgo import agent
from dlgo import goboard
from dlgo import gotypes
from dlgo.utils import print_board, print_move


def main():
    board_size = 9
    game = goboard.GameState.new_game(board_size)
    bots = {
        gotypes.Player.black: agent.RandomBot(),
        gotypes.Player.white: agent.RandomBot(),
    }
    while not game.is_over():
        print_board(game.board)
        bot_move = bots[game.next_player].select_move(game)
        print_move(game.next_player, bot_move)
        game = game.apply_move(game.next_player, bot_move)


if __name__ == '__main__':
    main()
# end::bot_vs_bot[]
