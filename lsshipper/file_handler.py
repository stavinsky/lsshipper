import asyncio
from .connection import logstash_connection
from .common.utils import get_files_to_update, line_to_json
from functools import partial
from lsshipper.logfile import LogFile
import logging
logger = logging.getLogger(name="general")


async def ship(f, state, queue, fields={}):
    logger.info("working with file:{}".format(f.name))
    async for line in f.get_line():
        if state.need_shutdown:
            f.sync_to_db(mtime_update=False)
            try:
                logger.warning("waiting for deliver all message")
                await asyncio.wait_for(queue.join(), timeout=60)
            except asyncio.TimeoutError:
                logger.error("not all message was delivered")
            return
        if len(line.strip()) > 0:
            message = line_to_json(f.name, line, f.offset, fields)
            while not state.need_shutdown:
                try:
                    await asyncio.wait_for(
                        queue.put(message),
                        timeout=1)
                    break
                except asyncio.TimeoutError:
                    pass
    logger.info(
        "file reading is finished, file: {}".format(f.name))
    f.sync_to_db(mtime_update=True)


class FileHandler(object):
    def __init__(self, loop, state, config):
        self.files_in_work = set()
        self.loop = loop
        self.queue = asyncio.Queue(maxsize=10, loop=self.loop)
        self.state = state
        self.config = config
        self.con = asyncio.ensure_future(
            logstash_connection(queue=self.queue, state=self.state,
                                loop=self.loop, config=self.config))

    async def start(self):
        while not self.state.need_shutdown:
            logger.debug("files in work: {}".format(self.files_in_work))
            files = await get_files_to_update(
                self.loop,
                self.config['files']['dir_path'],
                self.config['files']['pattern']
            )
            files = [LogFile(**f, config=self.config) for f in files
                     if f['name'] not in self.files_in_work]
            for f in files:
                f.sync_from_db()
                if not f.need_update:
                    continue
                task = asyncio.ensure_future(
                    ship(f, self.state, self.queue, self.config['fields']))
                task.add_done_callback(partial(
                    lambda name, _: self.files_in_work.remove(name), f.name))
                self.files_in_work.add(f.name)
            await asyncio.sleep(3.14)
            logger.debug("queue size: {}".format(self.queue.qsize()))
        await self.con

    async def run_once(self):
        files = await get_files_to_update(
            self.loop,
            self.config['files']['dir_path'],
            self.config['files']['pattern']
        )
        files = [LogFile(**f, config=self.config) for f in files]
        for f in files:
            if self.state.need_shutdown:
                break
            f.sync_from_db()
            if f.need_update:
                await ship(f, self.state, self.queue, self.config['fields'])
        self.state.shutdown()
        await self.con
