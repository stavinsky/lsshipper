import os
import re
import asyncio
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from logfile import LogFile
from config import config
from connection import logstash_connection
from utils import get_files_to_update
import logging
logger = logging.getLogger(name="general")


class MainHandler(object):
    def __init__(self, loop, state):
        self.files_in_work = set()
        self.loop = loop
        self.queue = asyncio.Queue(maxsize=10, loop=self.loop)
        self.tasks = list()
        self.state = state

    async def ship(self, f):
        async for line, offset in f.get_line():

            if self.state.need_shutdown:
                f.sync_to_db(mtime_update=False)
                break
            if line:
                message = f.line_to_json(line, offset)
                while not self.state.need_shutdown:
                    try:
                        await asyncio.wait_for(
                            self.queue.put(message),
                            timeout=20)
                        break
                    except asyncio.TimeoutError:
                        logger.debug("Queue is full, timeout on put")
            if line is None:  # if line is None we got last line
                logger.debug(
                    "file reading is finished, file: {}".format(f.name))
                f.sync_to_db(mtime_update=True)

        self.files_in_work.remove(f.name)

    async def start(self):
        pattern = re.compile(config['file_names_regexp'])
        line_separator = config["line_separator"].encode()
        asyncio.ensure_future(logstash_connection(
            queue=self.queue, state=self.state, loop=self.loop,
            use_ssl=config['ssl'], host=config['host'], port=config['port']
        ))
        while not self.state.need_shutdown:
            files = await get_files_to_update(
                self.loop, config['files_path'], pattern, line_separator)
            for f in files:
                if f.name in self.files_in_work:
                    continue
                f.sync_from_db()
                if not f.need_update:
                    continue
                self.tasks.append(asyncio.ensure_future(self.ship(f)))
                self.files_in_work.add(f.name)
            self.tasks = list(task for task in self.tasks if not task.done())
            await asyncio.sleep(3.14)
            logger.info("queue size: {}".format(self.queue.qsize()))

        while self.tasks:
            self.tasks = list(task for task in self.tasks if not task.done())
            logger.info("stopping task")
            await asyncio.sleep(0.1)
