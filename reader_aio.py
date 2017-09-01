import os
import aiofiles


class FileReader(object):
    def __init__(self, filename, offset=0, sep=b'\r\n'):
        self.name = os.path.abspath(filename)
        self.offset = 0
        self.sep = sep  # line separator

    async def get_line(self, chunk_size=4096):
        async with aiofiles.open(self.name, 'r+b') as f:
            await f.seek(self.offset)
            tmp_line = b""
            cont = True
            while cont:
                chunk = await f.read(chunk_size)
                if not chunk:
                    yield (None, self.offset)
                    break
                if chunk[-1] == 0:
                    cont = False
                if len(tmp_line):
                    chunk = tmp_line + chunk
                    tmp_line = b''
                while chunk:
                    line, sep, chunk = chunk.partition(self.sep)
                    if sep is self.sep:
                        self.offset = self.offset + len(line) + len(self.sep)
                        yield (line, self.offset)
                    if sep is b'':
                        tmp_line = tmp_line + line
                if not cont:
                    yield (None, self.offset)
