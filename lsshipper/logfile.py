import json
from .reader_aio import get_line
from .database import DataBase
import os


class LogFile:
    def __init__(self, name, mtime=0, offset=0, config={}):
        self.name = name
        self.mtime = mtime  # Current modify time from db
        self.last_mtime = 0   # Modify time from os.stat
        self.offset = offset
        self.db_file = config['database']["file"]
        self.sep = config['files']['newline']

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = os.path.abspath(name)

    @property
    def need_update(self):
        return self.mtime > self.last_mtime

    def sync_from_db(self,):
        with DataBase(self.db_file) as db:
            db.insert_ignore_file(self.name, 0)
            f = db.get_file(self.name)
        self.offset = f[2]
        self.last_mtime = f[1]

    def sync_to_db(self, mtime_update=False):
        if mtime_update:
            self.last_mtime = self.mtime
        with DataBase(self.db_file) as db:
            db.update_file(self.name, self.offset, self.last_mtime)

    def line_to_json(self, line, offset):
        data = {
            "message": line.decode('utf-8', 'replace'),
            "fields": {
                "program": 'mt4'
            },
            "source": self.name,
            "offset": offset,
        }
        return json.dumps(data) + '\n'

    async def get_line(self):
        async for line, offset in get_line(
                self.name, offset=self.offset, sep=self.sep):
            self.offset = offset
            yield line

    def __repr__(self):
        return "<LogFile: {}, {}, {}>".format(
            self.name, self.mtime, self.offset)
