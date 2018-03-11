# tag::gtp_coords_imports[]
from dlgo.gotypes import Point
from dlgo.goboard_fast import Move
# end::gtp_coords_imports[]

__all__ = [
    'coords_to_gtp_position',
    'gtp_position_to_coords',
]

COLS = 'ABCDEFGHJKLMNOPQRST'

"""Convert (row, col) tuple to GTP board locations.

Example:
>>> coords_to_gtp_position((1, 1))
'A1'
"""


# tag::gtp_coords_to_pos[]
def coords_to_gtp_position(move):
    point = move.point
    return COLS[point.col - 1] + str(point.row)
# end::gtp_coords_to_pos[]


"""Convert a GTP board location to a (row, col) tuple.

Example:
>>> gtp_position_to_coords('A1')
(1, 1)
"""


# tag::gtp_pos_to_coords[]
def gtp_position_to_coords(gtp_position):
    col_str, row_str = gtp_position[0], gtp_position[1:]
    point = Point(int(row_str), COLS.find(col_str.upper()) + 1)
    return Move(point)
# end::gtp_pos_to_coords[]
