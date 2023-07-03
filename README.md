# pWebServer

Small, asynchronous web server for use with Raspberry Pi Pico W boards and similar

### Notes
This library is not designed to be particularly fast, however it is intended to be easy to use.

**Example (micropython):**
```py
from pWebServer import Server
import uasyncio as asyncio

sv = Server()
sv.add_default_route() # simply adds a route at / that returns 200 OK
loop = asyncio.get_event_loop()
loop.create_task(sv.start()) # Start serving for 0.0.0.0 (all ipv4 ips) on port 80
```

## Requirements

python >=3.11 or micropython >=1.20

## installing

### python (with pypi)

```sh
pip install pWebServer
```

### micropython (with mip & url)

Using repl:
```py
import mip
mip.install("github:sjsadowski/pWebServer", version="latest")
```

Using mpremote:
```sh
mpremote mip install github:sjsadowski/pWebServer
```

## Dependencies

### MicroPython
MicroPython does not ship with the full set of Python Standard Libraries. For information about this, check the [micropython-lib GitHub repo](https://github.com/micropython/micropython-lib) .

- logging

### Python

** None **

## To Do:
- Cookie support
- HTTP/2.0(?)
- Better test coverage