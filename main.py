import asyncio

from mhd import server


if __name__ == "__main__":
    host, port = "localhost", 8080 # TODO: configurable
    loop = asyncio.get_event_loop()
    srv = server.listen(host, port)
    loop.run_until_complete(srv)
    try:
        loop.run_forever()
    finally:
        loop.close()
