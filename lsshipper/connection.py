import asyncio
import socket
import ssl
import logging
import async_timeout
import contextlib


logger = logging.getLogger(name="general")


def get_ssl_context(
        enable=False, cafile=None, client_crt=None, client_key=None):
    if not enable:
        return None
    ssl_context = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH, cafile=cafile)
    ssl_context.check_hostname = False
    ssl_context.load_cert_chain(client_crt, client_key)
    return ssl_context


async def get_message_from_queue(queue):
    with contextlib.suppress(asyncio.TimeoutError):
        async with async_timeout.timeout(1):
            message = await queue.get()
            return message


async def get_connection(host, port, ssl_context=None):
    try:
        reader, writer = await asyncio.open_connection(
            host=host, port=port,
            ssl=ssl_context,
            family=socket.AF_INET)
        return reader, writer
    except ConnectionError:
        logger.debug(
            ("cant connect to {}:{}, "
             "going to try again").format(
                host, port))
        return None, None


async def logstash_connection(queue, state, loop, config):
    ssl_context = get_ssl_context(
        enable=config['ssl']['enable'], cafile=config['ssl'].get('cafile'),
        client_crt=config['ssl'].get('client_crt'),
        client_key=config['ssl'].get('client_key'),
    )
    message = None
    need_reconnect = True
    host = config["connection"]['host']
    port = config["connection"]['port']
    while (state.need_shutdown is False) or queue.qsize() > 0:
        if need_reconnect:
            if state.need_shutdown:
                return
            logger.info("connecting to server")
            conn = None
            reader, writer = await get_connection(
                host, port, ssl_context=ssl_context)
        if reader is None:
            logger.info("reconnecting")
            await asyncio.sleep(1)
            need_reconnect = True
            continue

        if not message:
            message = await get_message_from_queue(queue)
            if not message:
                continue
        try:
            writer.write(message.encode())
            await writer.drain()
        except ConnectionError:
            need_reconnect = True
            continue
        if reader.at_eof():
            logger.error("Server disconnected while transfer")
            need_reconnect = True
        else:
            message = None
            need_reconnect = False

    if conn:
        _, writer = conn
        writer.close()
