import asyncio

from http.client import responses
from asyncio import coroutine as async


class Request(object):

    def __init__(self, method, uri, headers, body):
        self.method = method.upper()
        self.uri = uri
        self.headers = headers
        self.body = body


class Response(object): # TODO: verify order? (status < headers < body)

    def __init__(self, stream):
        self.stream = stream
        self._meta_over = False

    def status(self, status_code):
        reason_phrase = responses[status_code]
        status_code = bytes(str(status_code), encoding="ascii") # XXX: inefficient!?
        reason_phrase = bytes(reason_phrase, encoding="ascii") # XXX: encoding?
        self._writeline(b" ".join((b"HTTP/1.1", status_code, reason_phrase)))

    def header(self, name, value):
        name = bytes(_normalize_header(name), encoding="ascii") # XXX: encoding?
        value = bytes(value, encoding="utf-8") # XXX: encoding?
        self._writeline(b": ".join((name, value)))

    def body(self, data):
        if not self._meta_over:
            self._writeline(b"")
            self._meta_over = True
        self.stream.write(data)

    def _writeline(self, data):
        self.stream.write(data + b"\r\n")


@async
def process_request(input_stream, output_stream, request_handler):
    req = yield from _parse_request(input_stream)
    res = Response(output_stream)
    yield from request_handler(req, res)
    output_stream.close()


@async
def _parse_request(input_stream):
    request_line = yield from input_stream.readline()
    method, uri, _ = request_line.strip().split(b" ") # XXX: brittle? -- TODO: decode (encoding?)

    headers = yield from _extract_headers(input_stream)

    return Request(method, uri, headers, input_stream)


@async
def _extract_headers(input_stream):
    headers = {}
    while True:
        line = yield from input_stream.readline()
        line = line.strip()
        if line == b"":
            break

        name, value = line.split(b":", 1)
        name = _normalize_header(name.decode("ascii").strip()) # TODO: move normalization into `Request`
        value = value.decode("utf-8").strip() # XXX: UTF-8 as de-facto standard?
        headers[name] = value

    return headers


def _normalize_header(name): # XXX: overly simplistic?
    return "-".join(part.capitalize() for part in name.split("-"))
