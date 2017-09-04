import os
from lsshipper.logfile import LogFile
from concurrent.futures import ThreadPoolExecutor
from functools import partial


def get_files_list(config):
    files_conf = config['files']
    pattern = files_conf['pattern']
    dir_path = files_conf["dir_path"]
    files = list()
    for name in os.listdir(dir_path):
        if pattern.match(name):
            full_path = os.path.join(dir_path, name)
            f = LogFile(
                full_path,
                mtime=os.stat(full_path).st_mtime,
                config=config)
            files.append(f)

    return files


async def get_files_to_update(loop, config):

    with ThreadPoolExecutor() as executor:
        files = await loop.run_in_executor(
            executor, partial(get_files_list, config))
    return files
