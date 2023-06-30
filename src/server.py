import sys
import logging

# Conditional import
if sys.version.find('MicroPython') > -1:
    import uasyncio as asyncio # type: ignore
else:
    import asyncio

from asyncio import StreamReader, StreamWriter

class Request:

    # headers is a list of tuples with the header name and its value
    request: tuple = ()
    headers: list = []
    query_params: list = []
    body: str = ''

    def __init__(self) -> None:
        pass

    # parse the request
    # TODO: store query params
    # TODO: Process form data
    # TODO: Store body
    async def parse(self, reader: StreamReader):
        '''Parse an html text request
        '''
        await self._parse_request(reader)
        await self._parse_headers(reader)
        await self._parse_body(reader)


    async def _parse_headers(self, reader: StreamReader) -> None:
        '''(Private) parse request headers
        '''
        # The below reads the incoming request until it hits an empty line
        header_lines = reader.readuntil(b"\r\n\r\n")
        for header_line in header_lines.split(b"\r\n"):
            # done
            if header_line == b"\r\n":
                break
            key, value = header_line.decode('utf-8').strip().split(':')
            self.headers.append((key, value))



    async def _parse_request(self, reader: StreamReader = None) -> None:
        '''(private) parse request line and determine method, path, and query params
        '''
        if not reader:
            reader = self.reader

        if not reader:
            raise ValueError('No StreamReader supplied')
        logging.debug("parsing request")
        request_line = await reader.readline()
        logging.debug("Request:", request_line)


    async def _parse_body(self, reader: StreamReader):
        '''(private) parse body
        '''
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

        # parse the request
        req = Request(reader)
        req.parse()

        res = Response()
        res.generate(req)

        writer.write
        writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        # writer.write(response)
        writer.write('')
        await writer.drain()
        await writer.wait_closed()
        print("Client disconnected")

