# pWebServer

Small, asynchronous web server for use with Raspberry Pi Pico W boards and similar

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
mpremote mip install github:org/repo@branch-or-tag
```

## Dependencies

### MicroPython
MicroPython does not ship with the full set of Python Standard Libraries. For information about this, check the [micropython-lib GitHub repo](https://github.com/micropython/micropython-lib) .

- logging

### Python

** None **

