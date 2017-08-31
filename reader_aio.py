import sys
import os
import aiofiles
from config import config


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


async def print_lines():
    reader = FileReader(filename="test_files/20170829.log", sep=b"\n")
    async for line, offset in reader.get_line():
        if line:
            sys.stdout.write(
                line.decode(config['file_encoding'], "replace") + "\n")


if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(print_lines())
    loop.close()
