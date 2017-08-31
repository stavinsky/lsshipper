import sys
import os
import aiofiles
from config import config


def_sep = b'\r\n'
def_sep = b'\n'


class ReturnCode:
    ok = 0
    eof = 1
    zero = 2


class FileReader(object):
    def __init__(self, filename, offset=0):
        self.name = os.path.abspath(filename)
        self.offset = 0

    async def get_line(self, chunk_size=8196):
        async with aiofiles.open(self.name, 'r+b') as f:
            while True:
                await f.seek(self.offset)
                chunk = await f.read(chunk_size)
                chunk_lengh = len(chunk)
                if not chunk:
                    yield (None, self.offset, ReturnCode.eof)
                    break
                while chunk:
                    line, sep, chunk = chunk.partition(def_sep)
                    if line and line[-1] == 0:
                        yield (None, self.offset, ReturnCode.zero)
                    if sep == def_sep:
                        self.offset += len(line) + len(sep)
                        yield (line, self.offset, ReturnCode.ok)
                if chunk_lengh < chunk_size:
                    yield (None, self.offset, ReturnCode.eof)
                    break


async def print_lines():
    reader = FileReader(filename="test_files/test1.txt")
    async for line, offset, code in reader.get_line():
        if code == ReturnCode.ok:
            sys.stdout.write(
                line.decode(config['file_encoding'], "replace") + '\n')
            pass

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(print_lines())
    loop.close()
