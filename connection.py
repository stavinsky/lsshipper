import asyncio
from socket import error as socket_error
import socket
import errno
from config import config
import ssl
import logging

logger = logging.getLogger(name="connection")


def get_ssl_context():
    ssl_context = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH, cafile=config['cafile'])
    ssl_context.check_hostname = False
    ssl_context.load_cert_chain(config['client_crt'], config['client_key'])
    return ssl_context


async def get_message_from_queue(queue):
    message = None
    try:
        message = await asyncio.wait_for(queue.get(), timeout=1)
    except asyncio.TimeoutError:
        pass
    return message


async def logstash_connection(queue, state, loop, host, port,
                              use_ssl=False, message=None):

    if state.need_shutdown:
        return
    try:
        logger.debug("connecting to {}:{}".format(host, port))
        ssl = get_ssl_context() if use_ssl else None
        reader, writer = await asyncio.open_connection(
            host=host, port=port,
            ssl=ssl,
            family=socket.AF_INET)
        logger.debug("connected to {}:{}".format(host, port))

    except socket_error as serror:
        # if serror.errno == errno.ECONNREFUSED:
        logger.debug(
            "cant connect to {}:{}, going to try again".format(host, port))
        asyncio.ensure_future(
            logstash_connection(queue, state, loop, host, port,
                                use_ssl=use_ssl, message=message))
        await asyncio.sleep(10)
        return
    while not state.need_shutdown:
        if message is None:
            message = await get_message_from_queue(queue)
        if not message:
            continue
        logger.debug("got message from queue")
        logger.debug("sending message to logstash")

        try:
            writer.write(message.encode())
            await writer.drain()
            if reader.exception():
                raise Exception("Connection ERROR")
            logger.debug("sent ok")
        except Exception as e:
            logger.debug("Exception: {}".format(e))
            asyncio.ensure_future(
                logstash_connection(queue, state, loop, host, port,
                                    use_ssl=use_ssl, message=message))
            break

        message = None
        queue.task_done()
