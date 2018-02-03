__all__ = [
    'Response',
    'error',
    'serialize',
    'success',
]


class Response(object):
    """Response to a GTP command."""
    def __init__(self, status, body):
        self.success = status
        self.body = body


def success(body=''):
    """Make a successful GTP response."""
    return Response(status=True, body=body)


def error(body=''):
    """Make an error GTP response."""
    return Response(status=False, body=body)


def serialize(gtp_command, gtp_response):
    """Serialize a GTP response as a string.

    Needs the command we are responding to so we can match the sequence
    number.
    """
    return '%s%s %s\n\n' % (
        '=' if gtp_response.success else '?',
        '' if gtp_command.sequence is None else str(gtp_command.sequence),
        gtp_response.body,
    )
