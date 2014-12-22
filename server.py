import asyncio

from asyncio import coroutine as async


@async
def start_server(host, port):
    yield from asyncio.start_server(process_request, host, port)


@async
def process_request(reader, writer):
    request_line = yield from reader.readline()
    method, path, _ = request_line.strip().split(b" ") # XXX: brittle? -- TODO: decode (encoding?)
    print(">", method, path)

    headers = yield from extract_headers(reader)
    print(">", headers)


@async
def extract_headers(reader):
    headers = {}
    while True:
        line = yield from reader.readline()
        line = line.strip()
        if line == b"":
            break

        name, value = line.split(b":", 1)
        name = name.decode("ascii").strip() # TODO: normalize capitalization
        value = value.decode("utf-8").strip() # XXX: UTF-8 as de-facto standard?
        headers[name] = value

    return headers


if __name__ == "__main__":
    host, port = "localhost", 8080 # TODO: configurable
    loop = asyncio.get_event_loop()
    srv = start_server(host, port)
    loop.run_until_complete(srv)
    try:
        loop.run_forever()
    finally:
        loop.close()
