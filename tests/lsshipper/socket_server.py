import asyncio
import sys


async def handle_echo(reader, writer):
    # addr = writer.get_extra_info('peername')
    line = " "
    while line:
        line = await reader.readline()
        sys.stdout.write(line.decode())
        break
    writer.close()


loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo, '127.0.0.1', 5045, loop=loop)
server = loop.run_until_complete(coro)


try:
    loop.run_forever()
except KeyboardInterrupt:
    pass


server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
