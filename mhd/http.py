import asyncio

from http.client import responses
from asyncio import coroutine as async


# FIXME:
# * constructor must not be coroutine (generator), but separate `init` is fugly
# * verify decorator combinations (coroutine + property) are correct
class Request(object):

    def __init__(self, input_stream):
        self._stream = input_stream

    @async
    def init(self):
        request_line = yield from self._stream.readline()
        method, uri, _ = request_line.strip().split(b" ") # XXX: brittle? -- TODO: decode (encoding?)
        self.method = method.upper()
        self.uri = uri

    @async
    @property
    def headers(self):
        if not getattr(self, "_headers", None):
            self._headers = yield from _extract_headers(self._stream)
        return self._headers

    @async
    @property
    def body(self):
        yield from self.headers() # ensures headers have been consumed
        return self._stream


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
    req = Request(input_stream)
    yield from req.init()
    res = Response(output_stream)
    yield from request_handler(req, res)
    output_stream.close()


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
