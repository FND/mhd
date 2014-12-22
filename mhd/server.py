import asyncio

from asyncio import coroutine as async

from . import http


@async
def listen(host, port):
    yield from asyncio.start_server(http.process_request, host, port)
