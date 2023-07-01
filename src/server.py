import sys
import logging

# Conditional import
if sys.version.find('MicroPython') > -1:
    import uasyncio as asyncio # type: ignore
else:
    import asyncio

from asyncio import StreamReader, StreamWriter

class NotFoundError(NotImplementedError):
    pass

class Request:

    # headers is a list of tuples with the header name and its value

    __slots__ = [
        '_reader',
        '_request',
        '_headers',
        '_query_params',
        '_preserve_body',
        '_body',
        '_standard_methods',
        '_unimplemented_methods'
    ]

    _reader: StreamReader
    _request: tuple
    _headers: list
    _query_params: list
    _preserve_body: bool
    _body: str
    _standard_methods: list

    def __init__(self, reader:StreamReader, preserve_body = False) -> None:
        self._standard_methods = ['GET','POST','PUT','PATCH','DELETE','CONNECT','OPTIONS','TRACE']
        self._unimplemented_methods = ['PATCH','CONNECT','TRACE']
        self._preserve_body = preserve_body
        self._reader = reader

    # parse the request
    # TODO: store query params
    # TODO: Process form data
    # TODO: Store body
    async def parse(self):
        '''Parse an http request
        '''
        self._request = await self._parse_request(self._reader)
        self._headers = await self._parse_headers(self._reader)
        self._body = await self._parse_body(self._reader)
        if self._request[0] in ['GET', 'DELETE']:
            if not self._preserve_body:
                logging.warn(f'Request: {self._request} includes a body where none is expected, discarding')
                self._body = ''
            else:
                logging.warn(f'Request: {self._request} includes a body where none is expected, but preserve_body is set')



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



    async def _parse_request(self, reader: StreamReader = None) -> tuple:
        '''(private) parse request line and determine method, path, and query params
        '''
        if not reader:
            reader = self.reader

        if not reader:
            raise ValueError('No StreamReader supplied')
        logging.debug("parsing request")
        request_bytes = await reader.readline()
        request_line = request_bytes.decode('utf-8')
        logging.debug(f"Request: {request_line}")
        # we should only get the method, the path, and the query string
        method, path, query_string = request_line.replace('?',' ').split(' ', 2)

        if method not in self._standard_methods:
            raise NotImplementedError(f'Method: {method} is not a standard method and not implemented')

        if method in self._unimplemented_methods:
            raise NotImplementedError(f'Method: {method} is not implemented')

        # HTTP encode the spaces in the query string, just in case
        query_string.replace(' ', '%20')
        return (method, path, query_string)

    async def _parse_body(self, reader: StreamReader):
        '''(private) parse body
        '''
        pass

class Response:

    slots = ('_code', '_body')

    _code: int
    _body: str

    def __init__(self, code: int = 200, body: str = '') -> None:
        self._code = code
        self._body = body

    async def start(self, req = None):
        pass


class Server:

    routes: list = []

    def __init__(self) -> None:
        pass

    def add_route(self, method: str, path: str, fn) -> None:
        self.routes.append((method, path, fn))


    async def find_route(self, method: str, path:str) -> callable:
        '''Find a route based on method and path
        '''

        # TODO: route logic
        route = None
        return route


    # get the reader and
    async def create_request(self, reader):
        req = Request()
        req.parse(reader)

    async def send_response(self, res: Response):
        #res.generate(req)

        self._writer.write(res)
        # writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        # # writer.write(response)
        # writer.write('')
        await self._writer.drain()
        await self._writer.wait_closed()

    async def serve(self, reader, writer):

        self._reader = reader
        self._writer = writer

        req = Request(self._reader)
        res = Response()
        # parse the request
        try:
            logging.debug('Parsing request')
            req.parse()
        except NotImplementedError as not_implemented:
            logging.warn(not_implemented)
            res = Response(code=500, body=not_implemented)
            self.send_response(res)




        logging.info("Client disconnected")

    async def start(self, address: str = "0.0.0.0", port: int = 80):
        '''Start the web server on adddress:port (default any:80)
        '''
        asyncio.create_task(asyncio.start_server(self.serve, address, port))
