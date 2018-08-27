# tag::importlib[]
import importlib
# end::importlib[]

__all__ = [
    'Encoder',
    'get_encoder_by_name',
]


# tag::base_encoder[]
class Encoder:
    def name(self):  # <1>
        raise NotImplementedError()

    def encode(self, game_state):  # <2>
        raise NotImplementedError()

    def encode_point(self, point):  # <3>
        raise NotImplementedError()

    def decode_point_index(self, index):  # <4>
        raise NotImplementedError()

    def num_points(self):  # <5>
        raise NotImplementedError()

    def shape(self):  # <6>
        raise NotImplementedError()

# <1> Lets us support logging or saving the name of the encoder our model is using.
# <2> Turn a Go board into a numeric data.
# <3> Turn a Go board point into an integer index.
# <4> Turn an integer index back into a Go board point.
# <5> Number of points on the board, i.e. board width times board height.
# <6> Shape of the encoded board structure.
# end::base_encoder[]


# tag::encoder_by_name[]
def get_encoder_by_name(name, board_size):  # <1>
    if isinstance(board_size, int):
        board_size = (board_size, board_size)  # <2>
    module = importlib.import_module('dlgo.encoders.' + name)
    constructor = getattr(module, 'create')  # <3>
    return constructor(board_size)

# <1> We can create encoder instances by referencing their name.
# <2> If board_size is one integer, we create a square board from it.
# <3> Each encoder implementation will have to provide a "create" function that provides an instance.
# end::encoder_by_name[]
