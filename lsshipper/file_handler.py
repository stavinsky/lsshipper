import asyncio
from .connection import logstash_connection
from .common.utils import get_files_to_update
import logging
logger = logging.getLogger(name="general")


class FileHandler(object):
    def __init__(self, loop, state, config):
        self.files_in_work = set()
        self.loop = loop
        self.queue = asyncio.Queue(maxsize=10, loop=self.loop)
        self.tasks = list()
        self.state = state
        self.config = config

    async def ship(self, f):
        async for line, offset in f.get_line():

            if self.state.need_shutdown:
                f.sync_to_db(mtime_update=False)
                try:
                    await asyncio.wait_for(self.queue.join(), timeout=10)
                    logger.warning("waiting for deliver all message")
                except:
                    logger.error("not all message was delivered")
                break
            if line:
                message = f.line_to_json(line, offset)
                while not self.state.need_shutdown:
                    try:
                        await asyncio.wait_for(
                            self.queue.put(message),
                            timeout=2)
                        break
                    except asyncio.TimeoutError:
                        pass
            if line is None:  # if line is None we got last line
                logger.debug(
                    "file reading is finished, file: {}".format(f.name))
                f.sync_to_db(mtime_update=True)

        self.files_in_work.remove(f.name)

    async def start(self):
        conn = asyncio.ensure_future(logstash_connection(
            queue=self.queue, state=self.state,
            loop=self.loop, config=self.config))
        while not self.state.need_shutdown:
            files = await get_files_to_update(
                self.loop, self.config)
            for f in files:
                if f.name in self.files_in_work:
                    continue
                f.sync_from_db()
                if not f.need_update:
                    continue
                logger.debug("working with file:{}".format(f.name))
                self.tasks.append(asyncio.ensure_future(self.ship(f)))
                self.files_in_work.add(f.name)
            self.tasks = list(task for task in self.tasks if not task.done())
            await asyncio.sleep(3.14)
            logger.info("queue size: {}".format(self.queue.qsize()))

        while self.tasks:
            self.tasks = list(task for task in self.tasks if not task.done())
            logger.info("stopping tasks, still {}".format(len(self.tasks)))
            await asyncio.sleep(0.3)
        await conn
