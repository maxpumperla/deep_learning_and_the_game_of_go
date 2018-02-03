__all__ = [
    'Agent',
]


# tag::agent[]
class Agent():
    """Interface for a go-playing bot."""
    def select_move(self, game_state):
        raise NotImplementedError()
# end::agent[]

    def diagnostics(self):
        return {}
