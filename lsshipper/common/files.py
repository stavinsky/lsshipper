import os
import logging
import asyncio
from lsshipper.reader_aio import get_line
from lsshipper.common.utils import line_to_json
from async_timeout import timeout
import contextlib

logger = logging.getLogger(name="files")


class File:
    def __init__(self, name, mtime=0, offset=0, last_mtime=0, sep="\r"):
        self.name = name
        self.mtime = mtime  # Current modify time from db
        self.last_mtime = 0   # Modify time from os.stat
        self.offset = offset
        self.sep = sep
        self.last_mtime = last_mtime

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = os.path.abspath(name)

    @property
    def need_update(self):
        return self.mtime > self.last_mtime

    def __repr__(self):
        return "<LogFile: {}, {}, {}>".format(
            self.name, self.mtime, self.offset)


async def ship(f, state, queue, fields={}):
    logger.info("working with file:{}".format(f.name))
    async for line, offset in get_line(
            f.name, f.offset, f.sep):
        if state.need_shutdown:
            return False
        if len(line.strip()):
            message = line_to_json(f.name, line, f.offset, fields)
            while not state.need_shutdown:
                with contextlib.suppress(asyncio.TimeoutError):
                    async with timeout(1):
                        await queue.put(message)
                        f.offset = offset
                        break
    logger.info(
        "file reading is finished, file: {}".format(f.name))
    return True
