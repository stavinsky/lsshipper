import asyncio
import socket
import ssl
import logging

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
    message = None
    try:
        message = await asyncio.wait_for(queue.get(), timeout=1)
        queue.task_done()
    except asyncio.TimeoutError:
        pass
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
        return None


async def send_message(reader, writer, message):
    if reader.at_eof():
        logger.error("Server disconnected while transfer")
        return True, message
    try:
        writer.write(message.encode())
        await writer.drain()
    except Exception as e:
        logger.error("Exception: {}".format(e))
        return True, message
    return False, None


async def logstash_connection(queue, state, loop, config):
    ssl_context = get_ssl_context(
        enable=config['ssl']['enable'], cafile=config['ssl'].get('cafile'),
        client_crt=config['ssl'].get('client_crt'),
        client_key=config['ssl'].get('client_key'),
    )

    message = None
    need_reconnect = True
    conn = None
    host = config["connection"]['host']
    port = config["connection"]['port']
    while (state.need_shutdown is False) or queue.qsize() > 0:
        if need_reconnect:
            if state.need_shutdown:
                return
            logger.info("connecting to server")
            conn = await get_connection(host, port, ssl_context=ssl_context)
        if not conn:
            logger.info("reconnecting")
            await asyncio.sleep(1)
            need_reconnect = True
            continue
        need_reconnect = False

        if not message:
            message = await get_message_from_queue(queue)

        if message:
            need_reconnect, message = await send_message(*conn, message)
    reader, writer = conn
    writer.close()
