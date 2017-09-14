import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import re


async def get_files_to_update(loop, dir_path, pattern):
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
    return files
