import os
import aiofiles


async def get_line(name, offset=0, sep=b'\r\n', chunk_size=4096):
    name = os.path.abspath(name)
    async with aiofiles.open(name, 'r+b') as f:
        await f.seek(offset)
        tmp_line = b""
        chunk = await f.read(chunk_size)
        while chunk:
            if len(tmp_line):
                chunk = tmp_line + chunk
                tmp_line = b''
            while chunk:
                line, s, chunk = chunk.partition(sep)
                if 0 in line:
                    return
                if s is sep:
                    offset = offset + len(line) + len(sep)
                    yield (line, offset)
                if s is b'':
                    tmp_line = tmp_line + line
            chunk = await f.read(chunk_size)
