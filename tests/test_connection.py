import pytest
import asyncio
from common.state import State
from connection import logstash_connection
from common.config import config

counter = 0


@pytest.mark.asyncio
async def test_read_common_file(event_loop, unused_tcp_port):
    test = list()
    state = State()
    global counter
    counter = 0

    async def handler(reader, writer):
        global counter
        counter += 1
        while not state.need_shutdown:
            line = await reader.readline()
            if not line or line == b'':
                break
            if (counter % 2) == 0:
                writer.close()
                return
            test.append(line)
        done.set()
        writer.close()

    port = unused_tcp_port
    done = asyncio.Event()
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
        queue, state, loop=event_loop))
    await queue.join()
    state.shutdown()
    await client
    await done.wait()
    assert len(test) == len(test_messages)
    server.close()
    await server.wait_closed()
