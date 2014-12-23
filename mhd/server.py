import asyncio

from asyncio import coroutine as async

from . import http


def start_server(host, port, request_handler, loop=None):
    if not loop:
        loop = asyncio.get_event_loop()

    srv = _listen(host, port, request_handler)
    loop.run_until_complete(srv)
    try:
        loop.run_forever()
    finally:
        loop.close()


@async
def _listen(host, port, request_handler):
    srv = lambda req, res: http.process_request(req, res, request_handler)
    yield from asyncio.start_server(srv, host, port)
