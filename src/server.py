import sys

# Conditional import
if sys.version.find('MicroPython') > -1:
    import uasyncio as asyncio # type: ignore
else:
    import asyncio

class Server:

    routes: list = []

    def __init__(self) -> None:
        pass

    def add_route(self, method: str, path: str, fn) -> None:
        self.routes.append((method, path, fn))


    async def find_route(self, method: str, path:str) -> callable:
        pass


    async def serve(self):
        pass
