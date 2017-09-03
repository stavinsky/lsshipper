import asyncio
# from socket import error as socket_error
import socket
from .common.config import config
import ssl
import logging

logger = logging.getLogger(name="general")


def get_ssl_context():
    ssl_conf = config['ssl']
    if not ssl_conf['enable']:
        return None
    ssl_context = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH, cafile=ssl_conf['cafile'])
    ssl_context.check_hostname = False
    ssl_context.load_cert_chain(ssl_conf['client_crt'], ssl_conf['client_key'])
    return ssl_context


async def get_message_from_queue(queue):
    message = None
    try:
        message = await asyncio.wait_for(queue.get(), timeout=1)
    except asyncio.TimeoutError:
        pass
    return message


async def logstash_connection(queue, state, loop, message=None):
    conn = config["connection"]
    host = conn['host']
    port = conn['port']

    if state.need_shutdown:
        return

    try:
        reader, writer = await asyncio.open_connection(
            host=host, port=port,
            ssl=get_ssl_context(),
            family=socket.AF_INET)

    except ConnectionError as serror:
        logger.debug(
            ("cant connect to {}:{}, "
             "going to try again").format(
                host, port))
        await asyncio.sleep(5)
        asyncio.ensure_future(
            logstash_connection(queue, state, loop, message=None))
        return
    while not (state.need_shutdown and queue.qsize() == 0):
        if message is None:
            message = await get_message_from_queue(queue)
        if not message:
            continue

        if reader.at_eof():
            asyncio.ensure_future(
                logstash_connection(queue, state, loop, message=message))
            logger.error("Server disconnected")
            break
        try:
            writer.write(message.encode())
            await writer.drain()
        except Exception as e:
            logger.error("Exception: {}".format(e))
            asyncio.ensure_future(
                logstash_connection(queue, state, loop, message=message))
            break

        message = None
        queue.task_done()
