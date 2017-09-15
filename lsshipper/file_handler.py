import asyncio
from .connection import logstash_connection
from .common.utils import get_files, line_to_json
from functools import partial
from lsshipper.logfile import LogFile
import logging
from .database import DataBase
logger = logging.getLogger(name="general")


def sync_from_db(logfile, db_file):
    with DataBase(db_file) as db:
        db.insert_ignore_file(logfile.name, 0)
        f = db.get_file(logfile.name)
    logfile.offset = f[2]
    logfile.last_mtime = f[1]
    return logfile


def sync_to_db(logfile, db_file, finished=False):
    if finished:
        logfile.last_mtime = logfile.mtime
    with DataBase(db_file) as db:
        db.update_file(logfile.name, logfile.offset, logfile.last_mtime)


async def ship(f, state, queue, fields={}):
    logger.info("working with file:{}".format(f.name))
    finished = True
    async for line in f.get_line():
        if state.need_shutdown:
            finished = False
            break
        if len(line.strip()) > 0:
            message = line_to_json(f.name, line, f.offset, fields)
            while not state.need_shutdown:
                try:
                    await asyncio.wait_for(
                        queue.put(message),
                        timeout=1)
                    break
                except asyncio.TimeoutError:
                    finished = False
                # TODO remember prev offset and set it to the logfile object
    logger.info(
        "file reading is finished, file: {}".format(f.name))
    return finished


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

    async def get_files_to_upload(self):
        files = await get_files(
            self.loop,
            self.config['files']['dir_path'],
            self.config['files']['pattern']
        )
        files = [LogFile(**f, sep=self.config['files']['newline'])
                 for f in files if f['name'] not in self.files_in_work]
        for f in files:
            f = sync_from_db(f, self.config['database']['file'])
            if f.need_update:
                yield f

    async def start(self):
        def finished_callback(f, fut):
            self.files_in_work.remove(f.name)
            finished = fut.result()
            sync_to_db(f, self.config['database']['file'], finished=finished)

        while not self.state.need_shutdown:
            logger.debug("files in work: {}".format(self.files_in_work))

            async for f in self.get_files_to_upload():
                task = asyncio.ensure_future(
                    ship(f, self.state, self.queue, self.config['fields']))
                task.add_done_callback(partial(finished_callback, f))
                self.files_in_work.add(f.name)
            await asyncio.sleep(3.14)
            logger.debug("queue size: {}".format(self.queue.qsize()))
        await self.con

    async def run_once(self):
        async for f in self.get_files_to_upload():
            if self.state.need_shutdown:
                break
            if f.need_update:
                finished = await ship(
                    f, self.state, self.queue, self.config['fields'])
                sync_to_db(
                    f, self.config['database']['file'], finished=finished)

        self.state.shutdown()
        await self.con
