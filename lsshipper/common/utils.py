import os
from lsshipper.logfile import LogFile
from concurrent.futures import ProcessPoolExecutor
from functools import partial


def get_files_list(filepath, pattern, separator):
    files = list()
    for name in os.listdir(filepath):
        if pattern.match(name):
            full_path = os.path.join(filepath, name)
            f = LogFile(
                full_path,
                mtime=os.stat(full_path).st_mtime,
                sep=separator)  # have to be BytesArray
            files.append(f)

    return files


async def get_files_to_update(loop, filepath, pattern, line_separator):
    with ProcessPoolExecutor() as executor:
        files = await loop.run_in_executor(
            executor,
            partial(get_files_list,
                    filepath,
                    pattern,
                    line_separator))
    return files
