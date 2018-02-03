from ..gotypes import Point
from ..goboard_fast import Move

__all__ = [
    'coords_to_gtp_position',
    'gtp_position_to_coords',
]

# 'I' is intentionally omitted.
COLS = 'ABCDEFGHJKLMNOPQRST'


def coords_to_gtp_position(move):
    """Convert (row, col) tuple to GTP board locations.

    Example:
    >>> coords_to_gtp_position((0, 0))
    'A1'
    """
    point = move.point
    # coords are zero-indexed, GTP is 1-indexed.
    return COLS[point.col] + str(point.row + 1)


def gtp_position_to_coords(gtp_position):
    """Convert a GTP board location to a (row, col) tuple.

    Example:
    >>> gtp_position_to_coords('A1')
    (0, 0)
    """
    col_str, row_str = gtp_position[0], gtp_position[1:]
    point = Point(int(row_str) - 1, COLS.find(col_str))
    return Move(point)
