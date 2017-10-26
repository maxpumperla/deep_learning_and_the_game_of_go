__all__ = [
    'Agent',
]


# tag::agent[]
class Agent(object):
    """Interface for a go-playing bot."""
    def select_move(self, game_state):
        raise NotImplementedError()
# end::agent[]
