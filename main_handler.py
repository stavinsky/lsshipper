import os
import re
import asyncio
import janus
import ssl
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from logfile import LogFile
from config import config
from socket import error as socket_error
import socket
import errno

file_list_pattern = re.compile(config['file_names_regexp'])
ssl_context = ssl.create_default_context(
    ssl.Purpose.SERVER_AUTH, cafile=config['cafile'])
ssl_context.check_hostname = False
ssl_context.load_cert_chain(config['client_crt'], config['client_key'])


class MainHandler(object):
    def __init__(self, loop):
        self.files_in_work = set()
        self.stop_now = False
        self.loop = loop
        self.queue = asyncio.Queue(maxsize=10, loop=self.loop)
        self.tasks = list()

    @staticmethod
    def get_files_to_update():
        files = list()
        for name in os.listdir(config["files_path"]):
            if file_list_pattern.match(name):
                full_path = os.path.join(config["files_path"], name)
                f = LogFile(
                    full_path,
                    mtime=os.stat(full_path).st_mtime,
                )
                f.sync_from_db()
                files.append(f)

        return [f for f in files if f.need_update]

    async def ship(self, f):
        async for line, offset, code in f.get_line():
            if self.stop_now:
                f.sync_to_db(mtime_update=False)
                break
            if line:
                message = f.line_to_json(line, offset)
                while not self.stop_now:
                    try:
                        await asyncio.wait_for(
                            self.queue.put(message),
                            timeout=20)
                        break
                    except TimeoutError:
                        print("TimeOut")
            if not line:  # if line is None we got last line
                f.sync_to_db(mtime_update=True)

        self.files_in_work.remove(f.name)

    async def logstash_connection(self):
        try:
            reader, writer = await asyncio.open_connection(
                host=config['host'], port=config['port'],
                ssl=ssl_context, family=socket.AF_INET)

        except socket_error as serror:
            if serror.errno == errno.ECONNREFUSED:
                self.stop_now = True
                return
        while not self.stop_now:
            try:
                message = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=1)
            except TimeoutError:
                continue
            writer.write(message.encode())
            self.queue.task_done()

    async def start(self):
        asyncio.ensure_future(self.logstash_connection())
        while not self.stop_now:
            with ProcessPoolExecutor() as executor:
                files = await self.loop.run_in_executor(
                    executor, MainHandler.get_files_to_update)
            for f in files:
                if f.name not in self.files_in_work:
                    self.tasks.append(asyncio.ensure_future(self.ship(f)))
                    self.files_in_work.add(f.name)
            self.tasks = list(task for task in self.tasks if not task.done())
            await asyncio.sleep(3.14)
            print("queue size: ", self.queue.qsize())

        while self.tasks:
            self.tasks = list(task for task in self.tasks if not task.done())
            print(self.tasks)
            await asyncio.sleep(0.1)
