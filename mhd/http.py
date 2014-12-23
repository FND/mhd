import asyncio

from asyncio import coroutine as async


class Request(object):

    def __init__(self, method, path, headers, body):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body


@async
def process_request(input_stream, output_stream, request_handler):
    req = yield from _parse_request(input_stream)
    yield from request_handler(req, output_stream)
    output_stream.close()


@async
def _parse_request(input_stream):
    request_line = yield from input_stream.readline()
    method, path, _ = request_line.strip().split(b" ") # XXX: brittle? -- TODO: decode (encoding?)

    headers = yield from _extract_headers(input_stream)

    return Request(method, path, headers, input_stream)


@async
def _extract_headers(input_stream):
    headers = {}
    while True:
        line = yield from input_stream.readline()
        line = line.strip()
        if line == b"":
            break

        name, value = line.split(b":", 1)
        name = name.decode("ascii").strip() # TODO: normalize capitalization
        value = value.decode("utf-8").strip() # XXX: UTF-8 as de-facto standard?
        headers[name] = value

    return headers
