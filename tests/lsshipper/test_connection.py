import pytest
import asyncio
from lsshipper.common.state import State
from lsshipper.connection import logstash_connection
import logging


logging.basicConfig(level=logging.DEBUG)


@pytest.mark.asyncio
async def test_read_common_file(event_loop, unused_tcp_port):
    """transfer without disconnect"""
    test = list()
    state = State(event_loop)
    done = asyncio.Event()

    async def handler(reader, writer):
        while True:
            try:
                line = await reader.readline()
            except ConnectionError:
                break
            if not line or line == b'':
                break
            test.append(line.decode())
        done.set()
        writer.close()

    port = unused_tcp_port
    config = {}
    config['connection'] = {}
    config['ssl'] = {}
    config['connection']['host'] = '127.0.0.1'
    config['connection']['port'] = port
    config['ssl']['enable'] = False
    queue = asyncio.Queue(loop=event_loop)
    test_messages = list()

    for i in range(100):
        m = "Message {}\n".format(i)
        test_messages.append(m)
        await queue.put(m)
    server = await asyncio.start_server(
        handler, host='127.0.0.1', port=port, loop=event_loop)
    client = asyncio.ensure_future(logstash_connection(
        queue, state, event_loop, config), )
    await queue.join()
    state.shutdown()
    await done.wait()
    await client
    assert test == test_messages
    server.close()
    await server.wait_closed()
