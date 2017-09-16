import asyncio
import logging
import abc
from functools import partial
from lsshipper.connection import logstash_connection
from lsshipper.common.utils import get_files
from lsshipper.common.files import File, ship
from lsshipper.database import DataBase
logger = logging.getLogger(name="general")


class BaseUploader(metaclass=abc.ABCMeta):
    def __init__(self, loop, state, config):
        self.files_in_work = set()
        self.loop = loop
        self.state = state
        self.config = config
        self.queue = asyncio.Queue(maxsize=10, loop=self.loop)
        self.con = asyncio.ensure_future(
            logstash_connection(queue=self.queue, state=self.state,
                                loop=self.loop, config=self.config))

    async def get_files_to_upload(self):
        async for f in get_files(
                self.loop,
                self.config['files']['dir_path'],
                self.config['files']['pattern']):
            if f['name'] in self.files_in_work:
                continue
            with DataBase(self.config['database']['file']) as db:
                f = db.sync_from_db(f)
            f = File(**f, sep=self.config['files']['newline'])
            if f.need_update:
                yield f

    def end_of_upload(self, f, finished):
        self.files_in_work.remove(f.name)
        if finished:
            f.last_mtime = f.mtime
        with DataBase(self.config['database']['file']) as db:
            db.update_file(f.name, f.offset, f.last_mtime)

    @abc.abstractmethod
    def start():
        raise NotImplemented


class Uploader(BaseUploader):
    async def start(self):
        while not self.state.need_shutdown:
            logger.debug("files in work: {}".format(self.files_in_work))

            async for f in self.get_files_to_upload():
                task = asyncio.ensure_future(
                    ship(f, self.state, self.queue, self.config['fields']))
                task.add_done_callback(partial(
                    lambda f, fut: self.end_of_upload(f, fut.result()), f))
                self.files_in_work.add(f.name)
            await asyncio.sleep(3.14)
            logger.debug("queue size: {}".format(self.queue.qsize()))
        await self.con


class OneTimeUploader(BaseUploader):
    async def start(self):
        async for f in self.get_files_to_upload():
            if self.state.need_shutdown:
                break
            if f.need_update:
                self.files_in_work.add(f.name)
                finished = await ship(
                    f, self.state, self.queue, self.config['fields'])
                self.end_of_upload(f, finished)

        self.state.shutdown()
        await self.con
