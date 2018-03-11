"""GTP command.

A GTP command contains:
- An optional sequence number (used for matching up responses with
commands)
- A command name, e.g. 'genmove'
- One or more arguments to the command, e.g. 'black'
"""
__all__ = [
    'Command',
]


# tag::gtp_command[]
class Command(object):

    def __init__(self, sequence, name, args):
        self.sequence = sequence
        self.name = name
        self.args = tuple(args)

    def __eq__(self, other):
        return self.sequence == other.sequence and \
            self.name == other.name and \
            self.args == other.args

    def __repr__(self):
        return 'Command(%r, %r, %r)' % (self.sequence, self.name, self.args)

    def __str__(self):
        return repr(self)
# end::gtp_command[]


"""Parse a GTP protocol line into a Command object.

Example:
>>> parse('999 play white D4')
Command(999, 'play', ('white', 'D4'))
"""


# tag::parse_command[]
def parse(command_string):
    pieces = command_string.split()  # Check for the sequence number.
    try:
        sequence = int(pieces[0])
        pieces = pieces[1:]
    except ValueError:  # The first piece was non-numeric, so there was no sequence number.
        sequence = None
    name, args = pieces[0], pieces[1:]
    return Command(sequence, name, args)
# end::parse_command[]
