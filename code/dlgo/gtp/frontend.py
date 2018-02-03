from __future__ import absolute_import
import sys

from . import command, response
from .board import gtp_position_to_coords, coords_to_gtp_position
from ..goboard_fast import GameState

__all__ = [
    'GTPFrontend',
]

# Fixed handicap placement as defined in GTP spec.
HANDICAP_STONES = ['D4', 'Q16', 'D16', 'Q4', 'D10', 'Q10', 'K4', 'K16', 'K10']


class GTPFrontend(object):
    """Go Text Protocol frontend for a bot.

    Handles parsing GTP commands and formatting responses.

    Extremely limited implementation right now:
     - Only supports 19x19 boards.
     - Only supports fixed handicaps.
     - When white passes, black will pass too.
    """

    def __init__(self, agent):
        self.agent = agent
        self.game_state = GameState.new_game(19)
        self._input = sys.stdin
        self._output = sys.stdout
        self._stopped = False

    def run(self):
        while not self._stopped:
            ln = self._input.readline().strip()
            cmd = command.parse(ln)
            resp = self.process(cmd)
            self._output.write(response.serialize(cmd, resp))
            self._output.flush()

    def process(self, command):
        handlers = {
            'boardsize': self.handle_boardsize,
            'clear_board': self.handle_clear_board,
            'fixed_handicap': self.handle_fixed_handicap,
            'genmove': self.handle_genmove,
            'known_command': self.handle_known_command,
            'komi': self.ignore,
            'play': self.handle_play,
            'protocol_version': self.handle_protocol_version,
            'quit': self.handle_quit,
        }
        handler = handlers.get(command.name, self.handle_unknown)
        resp = handler(*command.args)
        return resp

    def ignore(self, *args):
        """Placeholder for commands we haven't dealt with yet."""
        return response.success()

    def handle_clear_board(self):
        self.game_state = GameState.new_game(19)
        return response.success()

    def handle_known_command(self, command_name):
        # TODO Should actually check if the command is known.
        return response.success('false')

    def handle_play(self, player, move):
        # color = 'b' if player == 'black' else 'w'
        if move != 'pass':
            self.game_state = self.game_state.apply_move(gtp_position_to_coords(move))
        return response.success()

    def handle_genmove(self, player):
        # bot_color = 'b' if player == 'black' else 'w'
        move = self.agent.select_move(self.game_state)
        if move is None:
            return response.success('pass')
        return response.success(coords_to_gtp_position(move))

    def handle_boardsize(self, size):
        if int(size) != 19:
            return response.error('Only 19x19 currently supported')
        return response.success()

    def handle_quit(self):
        self._stopped = True
        return response.success()

    def handle_unknown(self, *args):
        return response.error('Unrecognized command')

    def handle_fixed_handicap(self, nstones):
        nstones = int(nstones)
        for stone in HANDICAP_STONES[:nstones]:
            self.game_state = self.game_state.apply_move(gtp_position_to_coords(stone))
        return response.success()

    def handle_protocol_version(self):
        return response.success('2')
