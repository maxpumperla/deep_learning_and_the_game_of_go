__all__ = [
    'Response',
    'error',
    'serialize',
    'success',
]


# tag::gtp_response[]
class Response:
    def __init__(self, status, body):
        self.success = status
        self.body = body


def success(body=''):  # <1>
    return Response(status=True, body=body)


def error(body=''):  # <2>
    return Response(status=False, body=body)


def bool_response(boolean):  # <3>
    return success('true') if boolean is True else success('false')


def serialize(gtp_command, gtp_response):  # <4>
    return '{}{} {}\n\n'.format(
        '=' if gtp_response.success else '?',
        '' if gtp_command.sequence is None else str(gtp_command.sequence),
        gtp_response.body
    )
# <1> Making a successful GTP response with response body.
# <2> Making an error GTP response.
# <3> Converting a Python boolean into GTP.
# <4> Serialize a GTP response as a string.
# end::gtp_response[]
