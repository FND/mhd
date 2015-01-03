import asyncio

from http.client import responses
from asyncio import coroutine as async


# FIXME:
# * constructor must not be coroutine (generator), but separate `parse` is fugly
# * verify decorator combinations (coroutine + property) are correct
class Request:

    def __init__(self, input_stream):
        self._stream = input_stream

    @async
    def parse(self):
        request_line = yield from self._stream.readline()
        method, uri, _ = request_line.strip().split(b" ") # XXX: brittle?
        # NB: it's unclear which encodings should be supported here
        self.method = method.decode("ascii").upper()
        self.uri = uri.decode("ascii")

    @async
    def headers(self):
        if not getattr(self, "_headers", None):
            yield from self._extract_headers()
        return self._headers

    @async
    def body(self):
        yield from self.headers() # ensures headers have been consumed
        return self._stream

    @async
    def _extract_headers(self):
        headers = {}
        while True:
            line = yield from self._stream.readline()
            if line.strip() == b"":
                break

            name, value = [item.strip() for item in line.split(b":", 1)]
            name = _normalize_header(name.decode("ascii"))
            try:
                value = value.decode("ascii")
            except UnicodeDecodeError: # legacy support (cf. RFC 7230)
                value = value.decode("iso-8859-1")
            headers[name] = value

        self._headers = headers


class Response: # TODO: verify order? (status < headers < body)

    def __init__(self, stream):
        self.stream = stream
        self._meta_over = False

    def status(self, status_code):
        reason_phrase = responses[status_code]
        status_code = str(status_code).encode("ascii")
        reason_phrase = reason_phrase.encode("ascii")
        self._writeline(b" ".join((b"HTTP/1.1", status_code, reason_phrase)))

    def header(self, name, value):
        name = _normalize_header(name).encode("ascii")
        try:
            value = value.encode("ascii")
        except UnicodeDecodeError: # legacy support (cf. RFC 7230)
            value = value.encode("iso-8859-1")
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
    yield from req.parse()
    res = Response(output_stream)
    yield from request_handler(req, res)
    output_stream.close()


def _normalize_header(name): # XXX: overly simplistic?
    return "-".join(part.capitalize() for part in name.split("-"))
