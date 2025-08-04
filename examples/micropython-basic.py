from pWebServer import Server
import uasyncio as asyncio

sv = Server()
sv.add_default_route() # simply adds a route at / that returns 200 OK
loop = asyncio.get_event_loop()
loop.create_task(sv.start()) # Start serving for 0.0.0.0 (all ipv4 ips) on port 80
loop.run_forever()
