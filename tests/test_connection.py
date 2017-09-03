import pytest
import asyncio
from common.state import State
from connection import logstash_connection
from common.config import config


@pytest.mark.asyncio
async def test_read_common_file(event_loop, unused_tcp_port):
    test = list()
    state = State()

    async def handler(reader, writer):
        while not state.need_shutdown:
            line = await reader.readline()
            if not line or line == b'':
                break
            test.append(line)
        done.set()
        writer.close()

    port = unused_tcp_port
    done = asyncio.Event()
    config['connection']['host'] = '127.0.0.1'
    config['connection']['port'] = port
    config['ssl']['enable'] = False
    queue = asyncio.Queue(loop=event_loop)
    await queue.put("Message 1\n")
    await queue.put("Message 2\n")
    await queue.put("Message 3\n")
    server = await asyncio.start_server(
        handler, host='127.0.0.1', port=port, loop=event_loop)
    client = asyncio.ensure_future(logstash_connection(
        queue, state, loop=event_loop))
    await queue.join()
    state.shutdown()
    await client
    await done.wait()
    assert len(test) == 3
    server.close()
    await server.wait_closed()
