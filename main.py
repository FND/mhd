import asyncio

from asyncio import coroutine as async

from mhd.server import start_server


@async
def dispatch(req, res): # XXX: DEBUG; for demo purposes only
    res.status(200)
    res.header("Content-Length", "38")
    info = "%s %s\n" % (req.method, req.uri)
    res.body(info.encode("ascii"))
    res.body(b"lorem ipsum\ndolor sit amet\n\n...\n")


if __name__ == "__main__":
    host, port = "localhost", 8080 # TODO: configurable
    start_server(host, port, dispatch)
