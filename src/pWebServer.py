import sys
import json
import logging

# Conditional import
if sys.version.find('MicroPython') > -1:
    import uasyncio as asyncio # type: ignore
    from uasyncio import StreamReader, StreamWriter # type: ignore
else:
    import asyncio
    from asyncio import StreamReader, StreamWriter

logging.basicConfig(level=logging.DEBUG)


class NotFoundError(NotImplementedError):
    pass

class Request:
    '''Parses the request from the client
    '''

    # headers is a list of tuples with the header name and its value

    __slots__ = [
        '_reader',
        '_request',
        '_headers',
        '_query_params',
        '_preserve_body',
        '_body',
        '_standard_methods',
        '_unimplemented_methods',
        'method',
        'path',
        'query_string'
    ]

    _reader: StreamReader
    _request: tuple
    _headers: list
    _query_params: list
    _preserve_body: bool
    _body: str
    _standard_methods: list
    method: str
    path: str
    query_string: str

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
        self.method, self.path, self.query_string = self._request
        self._headers = await self._parse_headers(self._reader)
        self._body = await self._parse_body(self._reader)
        if self._request[0] in ['GET', 'DELETE']:
            if not self._preserve_body:
                logging.debug(f'Request: {self._request} includes a body where none is expected, discarding')
                self._body = ''
            else:
                logging.debug(f'Request: {self._request} includes a body where none is expected, but preserve_body is set')


    async def _parse_headers(self, reader: StreamReader) -> list:
        '''(Private) parse request headers
        '''
        # The below reads the incoming request until it hits an empty line
        header_lines: str = await reader.readuntil(b"\r\n\r\n")
        headers: list = []

        for header_line in header_lines.split(b"\r\n"):
            if header_line.decode('utf-8') == "\r\n":
                continue
            try:
                key, value = header_line.decode('utf-8').strip().split(':',1)
                headers.append((key, value))
            except ValueError:
                logging.debug("Discarding empty header value")


        return headers

    async def _parse_request(self, reader: StreamReader = None) -> tuple:
        '''(private) parse request line and determine method, path, and query params
        '''
        if not reader:
            reader = self._reader

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
        return ''

class Response:
    '''Builds a response to be sent to the client
    '''

    slots = ('_code', '_code_text', '_headers', '_body')

    _code: int
    _code_text: str
    _headers: list
    _body: str

    def __init__(self, code: int = 200, headers: list = [], body: str = '') -> None:
        if code not in HTTP_CODES.keys():
            raise NotImplementedError(f'HTTP code ({code}) not implemented')

        self._code = code
        self._code_text = HTTP_CODES[int(code)]
        self._headers = headers
        self._body = body

    def add_header(self, header: tuple):
        if not isinstance(header, tuple):
            raise ValueError('Header is not a tuple')

    def __str__(self) -> str:
        '''Return text for HTTP response
        '''
        headers: list = []

        response_line = f"HTTP/1.1 {self._code_text}\r\n"
        if len(self._headers) == 0:
            headers.append(('Content-Type','text/plain'))
        else:
            if 'Content-Type' not in [a[0] for a in self._headers]:
                headers.append(('Content-Type','text/plain'))


        header_list = [': '.join(h) for h in headers]
        headers = "\r\n".join(header_list)
        if self._body != '':
            body = f"\r\n\r\n{self._body}"
        else:
            body = self._code_text

        return f"{response_line}{headers}{body}"


class Server:
    '''Handles the actual incoming requests and sends a response
    '''

    __slots__ = ('routes', '_reader', '_writer')

    routes: list
    _writer: StreamWriter
    _reader: StreamReader

    def __init__(self) -> None:
        self.routes = []

    def add_route(self, method: str, path: str, fn: callable) -> None:
        '''Adds a function-based route
        '''
        self.routes.append((method, path, fn))


    # TODO: static route logic necessary
    def static_route(self, path: str, recursive: bool = True) -> None:
        '''Adds a static route - serves direct file content
        '''
        pass


    async def find_route(self, method: str, path:str) -> callable:
        '''Find a route based on method and path

        Returns first matching route
        '''

        # TODO: route logic
        print(self.routes)
        matched_routes = [route for route in self.routes if route[0] == method and route[1] == path]
        if len(matched_routes) == 0:
            raise NotFoundError(f'No route matched {method} {path}')
        else:
            route = matched_routes.pop(0)[2]
        return route


    # get the reader and
    async def create_request(self, reader):
        req = Request()
        req.parse(reader)

    async def send_response(self, res: Response):
        #res.generate(req)
        response_text = str(res).encode()
        logging.debug(f"Sending response: {res._code_text}")

        self._writer.write(response_text)
        # writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        # # writer.write(response)
        # writer.write('')
        await self._writer.drain()
        self._writer.close()
        await self._writer.wait_closed()
        print('Response sent')

    async def _serve(self, reader, writer):
        '''Find and serve the route
        '''

        self._reader = reader
        self._writer = writer

        req = Request(self._reader)
        # parse the request
        try:
            logging.debug('Parsing request')
            await req.parse()
        except NotImplementedError as not_implemented:
            logging.warn(not_implemented)
            res = Response(code=500, body=not_implemented)
            self.send_response(res)

        try:
            fn = await self.find_route(req.method, req.path)
            res = await fn(req)
        except NotFoundError as nfe:
            logging.warning(f"No route found for {req.method} {req.path}")
            res = Response(code=404)

        await self.send_response(res)

        logging.info("Client disconnected")

    def add_default_route(self) -> None:
        async def _default_route(request: Request) -> Response:
            res = Response(body='200 OK')
            return res

        self.add_route('GET', '/', _default_route)

    async def start(self, address: str = "0.0.0.0", port: int = 80):
        '''Start the web server on adddress:port (default any:80)
        '''
        if len(self.routes) == 0:
            raise NotImplementedError('There are no routes implemented')

        await asyncio.start_server(self._serve, address, port)

HTTP_CODES = {
    200: '200 OK',
    400: '400 Bad Request',
    401: '401 Unauthorized',
    403: '403 Forbidden',
    404: '404 Not Found',
    500: '500 Internal Server Error',
    503: '503 Service Unavailable'
}