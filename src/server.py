import sys
import logging

# Conditional import
if sys.version.find('MicroPython') > -1:
    import uasyncio as asyncio # type: ignore
else:
    import asyncio


class Request:

    # headers is a list of tuples with the header name and its value
    headers: list = []
    query_params: list = []
    body: str = ''

    def __init__(self) -> None:
        pass

    # parse the request
    # TODO: store query params
    # TODO: Process form data
    # TODO: Store body
    async def parse(self, reader):
        logging.debug("parsing request")
        request_line = await reader.readline()
        logging.debug("Request:", request_line)


        # The below reads the incoming request until it hits an empty line

        for header_line in reader.readline():
            if header_line == b"\r\n":
                break
            key, value = header_line.split(':')
            self.headers.append((key, value))

        request = str(request_line)

    async def _parse_headers():
        pass

    async def _parse_query():
        pass

class Response:
    pass


class Server:

    routes: list = []

    def __init__(self) -> None:
        pass

    def add_route(self, method: str, path: str, fn) -> None:
        self.routes.append((method, path, fn))


    async def find_route(self, method: str, path:str) -> callable:
        pass


    # get the reader and
    async def create_request(self, reader):
        req = Request()
        req.parse(reader)


    async def serve(self, reader, writer):


        writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        writer.write(response)

        await writer.drain()
        await writer.wait_closed()
        print("Client disconnected")

