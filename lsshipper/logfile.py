from .reader_aio import get_line


class LogFile:
    def __init__(self, name, mtime=0, offset=0, sep="\r"):
        self.name = name
        self.mtime = mtime  # Current modify time from db
        self.last_mtime = 0   # Modify time from os.stat
        self.offset = offset
        self.sep = sep

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = os.path.abspath(name)

    @property
    def need_update(self):
        return self.mtime > self.last_mtime

    async def get_line(self):
        async for line, offset in get_line(
                self.name, offset=self.offset, sep=self.sep):
            self.offset = offset
            yield line

    def __repr__(self):
        return "<LogFile: {}, {}, {}>".format(
            self.name, self.mtime, self.offset)
