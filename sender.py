import asyncio
import ssl
from config import config


class ClientProtocol(asyncio.Protocol):
    def __init__(self, message, queue):
        self.message = message
        self.queue = queue

    def connection_made(self, transport):
        message = self.queue.get()
        transport.write(self.message.encode("utf8"))
        print('Data sent: {!r}'.format(self.message))
        queue.task_done()

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()


ssl_context = ssl.create_default_context(
    ssl.Purpose.SERVER_AUTH, cafile=config['cafile'])
ssl_context.check_hostname = False
ssl_context.load_cert_chain(config['client_crt'], config['client_key'])
