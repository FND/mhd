import asyncio

from asyncio import coroutine as async

from mhd.server import start_server


@async
def dispatch(req, res): # XXX: DEBUG; for demo purposes only
    res.write(b" ".join((req.method, req.path)))
    #res.write(req.headers)
    #res.write(req.body)
    res.write(b"\nlorem ipsum\ndolor sit amet\n\n...")


if __name__ == "__main__":
    host, port = "localhost", 8080 # TODO: configurable
    start_server(host, port, dispatch)
