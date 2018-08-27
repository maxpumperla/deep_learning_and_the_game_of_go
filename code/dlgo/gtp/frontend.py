from __future__ import absolute_import
# tag::gtp_frontend_imports[]
import sys

from dlgo.gtp import command, response
from dlgo.gtp.board import gtp_position_to_coords, coords_to_gtp_position
from dlgo.goboard_fast import GameState, Move
from dlgo.agent.termination import TerminationAgent
from dlgo.utils import print_board
# end::gtp_frontend_imports[]

__all__ = [
    'GTPFrontend',
]

# Fixed handicap placement as defined in GTP spec.

"""Go Text Protocol frontend for a bot.

Handles parsing GTP commands and formatting responses.
Only supports 19x19 boards and fixed handicaps.
"""

# tag::gtp_frontend_init[]
HANDICAP_STONES = {
    2: ['D4', 'Q16'],
    3: ['D4', 'Q16', 'D16'],
    4: ['D4', 'Q16', 'D16', 'Q4'],
    5: ['D4', 'Q16', 'D16', 'Q4', 'K10'],
    6: ['D4', 'Q16', 'D16', 'Q4', 'D10', 'Q10'],
    7: ['D4', 'Q16', 'D16', 'Q4', 'D10', 'Q10', 'K10'],
    8: ['D4', 'Q16', 'D16', 'Q4', 'D10', 'Q10', 'K4', 'K16'],
    9: ['D4', 'Q16', 'D16', 'Q4', 'D10', 'Q10', 'K4', 'K16', 'K10'],
}


class GTPFrontend:

    def __init__(self, termination_agent, termination=None):
        self.agent = termination_agent
        self.game_state = GameState.new_game(19)
        self._input = sys.stdin
        self._output = sys.stdout
        self._stopped = False

        self.handlers = {
            'boardsize': self.handle_boardsize,
            'clear_board': self.handle_clear_board,
            'fixed_handicap': self.handle_fixed_handicap,
            'genmove': self.handle_genmove,
            'known_command': self.handle_known_command,
            'komi': self.ignore,
            'showboard': self.handle_showboard,
            'time_settings': self.ignore,
            'time_left': self.ignore,
            'play': self.handle_play,
            'protocol_version': self.handle_protocol_version,
            'quit': self.handle_quit,
        }
# end::gtp_frontend_init[]

# tag::gtp_frontend_run[]
    def run(self):
        while not self._stopped:
            input_line = self._input.readline().strip()
            cmd = command.parse(input_line)
            resp = self.process(cmd)
            self._output.write(response.serialize(cmd, resp))
            self._output.flush()

    def process(self, cmd):
        handler = self.handlers.get(cmd.name, self.handle_unknown)
        return handler(*cmd.args)
# end::gtp_frontend_run[]

# tag::gtp_frontend_commands[]
    def handle_play(self, color, move):
        if move.lower() == 'pass':
            self.game_state = self.game_state.apply_move(Move.pass_turn())
        elif move.lower() == 'resign':
            self.game_state = self.game_state.apply_move(Move.resign())
        else:
            self.game_state = self.game_state.apply_move(gtp_position_to_coords(move))
        return response.success()

    def handle_genmove(self, color):
        move = self.agent.select_move(self.game_state)
        self.game_state = self.game_state.apply_move(move)
        if move.is_pass:
            return response.success('pass')
        if move.is_resign:
            return response.success('resign')
        return response.success(coords_to_gtp_position(move))

    def handle_fixed_handicap(self, nstones):
        nstones = int(nstones)
        for stone in HANDICAP_STONES[nstones]:
            self.game_state = self.game_state.apply_move(
                gtp_position_to_coords(stone))
        return response.success()
# end::gtp_frontend_commands[]

    def handle_quit(self):
        self._stopped = True
        return response.success()

    def handle_clear_board(self):
        self.game_state = GameState.new_game(19)
        return response.success()

    def handle_known_command(self, command_name):
        return response.bool_response(command_name in self.handlers.keys())

    def handle_boardsize(self, size):
        if int(size) != 19:
            return response.error('Only 19x19 currently supported, requested {}'.format(size))
        return response.success()

    def handle_showboard(self):
        print_board(self.game_state.board)
        return response.success()

    def handle_time_left(self, color, time, stones):
        # TODO: Arguments: color color, int time, int stones
        return response.success()

    def handle_time_settings(self, main_time, byo_yomi_time, byo_yomi_stones):
        # TODO: Arguments: int main_time, int byo_yomi_time, int byo_yomi_stones
        return response.success()

    def handle_unknown(self, *args):
        return response.error('Unrecognized command')

    def ignore(self, *args):
        return response.success()

    def handle_protocol_version(self):
        return response.success('2')
