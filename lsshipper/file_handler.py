import asyncio
from .connection import logstash_connection
from .common.utils import get_files_to_update
from functools import partial
import logging
logger = logging.getLogger(name="general")


class FileHandler(object):
    def __init__(self, loop, state, config):
        self.files_in_work = set()
        self.loop = loop
        self.queue = asyncio.Queue(maxsize=10, loop=self.loop)
        self.state = state
        self.config = config

    async def ship(self, f):
        logger.info("working with file:{}".format(f.name))
        async for line, offset in f.get_line():
            if self.state.need_shutdown:
                f.sync_to_db(mtime_update=False)
                try:
                    logger.warning("waiting for deliver all message")
                    await asyncio.wait_for(self.queue.join(), timeout=60)
                except:
                    logger.error("not all message was delivered")
                break
            if line is None:  # if line is None we got last line
                logger.info(
                    "file reading is finished, file: {}".format(f.name))
                f.sync_to_db(mtime_update=True)
                break

            if len(line.strip()) > 0:
                message = f.line_to_json(line, offset)
                while not self.state.need_shutdown:
                    try:
                        await asyncio.wait_for(
                            self.queue.put(message),
                            timeout=2)
                        break
                    except asyncio.TimeoutError:
                        pass

    async def start(self):
        conn = asyncio.ensure_future(logstash_connection(
            queue=self.queue, state=self.state,
            loop=self.loop, config=self.config))
        while not self.state.need_shutdown:
            logger.debug("files in work: {}".format(self.files_in_work))
            files = await get_files_to_update(
                self.loop, self.config)

            for f in files:
                if f.name in self.files_in_work:
                    continue
                f.sync_from_db()
                if not f.need_update:
                    continue
                task = asyncio.ensure_future(self.ship(f))
                task.add_done_callback(partial(
                    lambda name, _: self.files_in_work.remove(name), f.name))
                self.files_in_work.add(f.name)
            await asyncio.sleep(3.14)
            logger.info("queue size: {}".format(self.queue.qsize()))
        await conn

    async def run_once(self):
        conn = asyncio.ensure_future(logstash_connection(
            queue=self.queue, state=self.state,
            loop=self.loop, config=self.config))
        files = await get_files_to_update(
            self.loop, self.config)
        for f in files:
            if self.state.need_shutdown:
                break
            f.sync_from_db()
            if f.need_update:
                await self.ship(f)
        self.state.shutdown()
        await conn
