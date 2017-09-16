import os
import re
import json
from concurrent.futures import ThreadPoolExecutor
from functools import partial


async def get_files(loop, dir_path, pattern):
    def get_files_list(dir_path, pattern):
        files = list()
        pattern = re.compile(pattern)
        with os.scandir(dir_path) as it:
            for fo in it:
                if fo.is_dir():
                    continue
                if pattern.match(fo.name):
                    full_path = os.path.join(dir_path, fo.name)
                    f = {
                        "name": full_path,
                        "mtime": fo.stat().st_mtime,
                    }
                    files.append(f)
        return files

    with ThreadPoolExecutor() as executor:
        files = await loop.run_in_executor(
            executor, partial(
                get_files_list, dir_path, pattern))
        for f in files:
            yield f


def line_to_json(name, line, offset, fields={}):
    data = {
        "message": line.decode('utf-8', 'replace'),
        "fields": fields,
        "source": name,
        "offset": offset,
    }
    return json.dumps(data) + '\n'
