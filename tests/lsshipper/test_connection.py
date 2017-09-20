import pytest
import asyncio
from lsshipper.common.state import State
from lsshipper.connection import logstash_connection


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
            except:
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


counter = 0


@pytest.mark.asyncio
# @pytest.mark.xfail(
#     reason="Cant make shure that all messages will be delivered")
async def test_read_common_file_with_disconnects(event_loop, unused_tcp_port):
    """transfer with disconnects"""
    test = list()
    state = State(event_loop)
    global counter
    done = asyncio.Event()
    counter = 0

    async def handler(reader, writer):
        global counter
        while True:
            counter += 1
            line = await reader.readline()
            if not line or line == b'':
                break

            test.append(line.decode())
            if counter % 6 == 0:
                writer.close()
                return
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
    sent_messages = list()

    for i in range(100):
        m = "Message {}\n".format(i)
        sent_messages.append(m)
        await queue.put(m)

    server = await asyncio.start_server(
        handler, host='127.0.0.1', port=port, loop=event_loop)
    client = asyncio.ensure_future(logstash_connection(
        queue, state, loop=event_loop, config=config))
    await queue.join()
    state.shutdown()
    await done.wait()
    await client
    assert len(test) == len(sent_messages)
    server.close()
    await server.wait_closed()
