from __future__ import absolute_import
from __future__ import print_function
import copy
import itertools
import json

from .archive import SGFLocator, find_sgfs, tarball_iterator
from ..goboard_fast import Board
from ..gosgf import Sgf_game
from six.moves import range

__all__ = [
    'CorpusIndex',
    'build_index',
    'load_index',
    'store_index',
]


def _sequence(game_record):
    """Extract game moves from a game record.

    The main sequence includes lots of stuff that is not actual game
    moves.
    """
    seq = []
    for item in game_record.get_main_sequence():
        color, move = item.get_move()
        # color == None is entries that are not actual game play
        # move == None is a pass, which in theory we could try to
        # predict, but not yet
        if color is not None and move is not None:
            seq.append((color, move))
    return seq


class CorpusIndex(object):
    def __init__(self, physical_files, chunk_size, boundaries):
        self.physical_files = list(sorted(physical_files))
        self.chunk_size = chunk_size
        self.boundaries = list(boundaries)

    @property
    def num_chunks(self):
        return len(self.boundaries)

    def serialize(self):
        return {
            'physical_files': self.physical_files,
            'chunk_size': self.chunk_size,
            'boundaries': [boundary.serialize() for boundary in self.boundaries],
        }

    @classmethod
    def deserialize(cls, serialized):
        return cls(
            serialized['physical_files'],
            serialized['chunk_size'],
            [Pointer.deserialize(raw_boundary) for raw_boundary in serialized['boundaries']])

    def get_chunk(self, chunk_number):
        assert 0 <= chunk_number < self.num_chunks
        chunk_start = self.boundaries[chunk_number]
        iterator = iter(self._generate_examples(chunk_start.locator))
        # Skip to the appropriate move in the current game.
        for _ in range(chunk_start.position):
            next(iterator)
        return itertools.islice(iterator, self.chunk_size)

    def _generate_examples(self, start):
        """
        Args:
            start (SGFLocator)
        """
        start_file_idx = self.physical_files.index(start.physical_file)
        for physical_file in self.physical_files[start_file_idx:]:
            for sgf in self._generate_games(physical_file):
                if sgf.locator < start:
                    continue
                board = Board(19, 19)
                try:
                    game_record = Sgf_game.from_string(sgf.contents)
                    # Set up the handicap.
                    if game_record.get_handicap() > 0:
                        for setup in game_record.get_root().get_setup_stones():
                            for move in setup:
                                board.apply_move('b', move)
                    for i, (color, move) in enumerate(_sequence(game_record)):
                        yield copy.deepcopy(board), color, move
                        if move is not None:
                            board.apply_move(color, move)
                except ValueError:
                    print(("Invalid SGF data, skipping game record %s" % (sgf,)))
                    print(("Board was:\n%s" % (board,)))

    def _generate_games(self, physical_file):
        with tarball_iterator(physical_file) as tarball:
            for sgf in tarball:
                yield sgf


class Pointer(object):
    """Identifies a specific training example inside a corpus."""
    def __init__(self, locator, position):
        self.locator = locator
        self.position = position

    def __str__(self):
        return '%s:%d' % (self.locator, self.position)

    def serialize(self):
        return {
            'locator': self.locator.serialize(),
            'position': self.position,
        }

    @classmethod
    def deserialize(cls, serialized):
        return cls(
            SGFLocator.deserialize(serialized['locator']),
            serialized['position']
        )


def build_index(path, chunk_size):
    """Index all SGF files found in the given location.
    This will include SGF that are contained inside zip or tar archives.
    """
    physical_files = set()
    boundaries = []
    examples_needed = 0
    for sgf in find_sgfs(path):
        physical_files.add(sgf.locator.physical_file)
        if examples_needed == 0:
            # The start of this SGF is a chunk boundary.
            boundaries.append(Pointer(sgf.locator, 0))
            examples_needed = chunk_size
        game_record = Sgf_game.from_string(sgf.contents)
        num_positions = len(_sequence(game_record))
        if examples_needed < num_positions:
            # The start of the next chunk is inside this SGF.
            boundaries.append(Pointer(sgf.locator, examples_needed))
            remaining_examples = num_positions - examples_needed
            examples_needed = chunk_size - remaining_examples
        else:
            # This SGF is entirely contained within the current chunk.
            examples_needed -= num_positions

    return CorpusIndex(physical_files, chunk_size, boundaries)


def load_index(input_stream):
    return CorpusIndex.deserialize(json.load(input_stream))


def store_index(index, output_stream):
    json.dump(index.serialize(), output_stream)
