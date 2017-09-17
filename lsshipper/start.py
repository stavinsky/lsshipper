from lsshipper.common.config import prepare_config
import asyncio
import signal
from functools import partial
import logging
import logging.config
from .common.state import State
from lsshipper.uploaders import Uploader, OneTimeUploader
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

signal_times = 0
logger = logging.getLogger('general')


def got_int_signal(state, signum, frame):
    global signal_times
    signal_times += 1
    logger.info("got term signal")
    state.shutdown()
    if signal_times > 1:
        logger.info("got term signal second time. Going to kill main loop")
        state.loop.close()


def main():
    config = prepare_config()
    loop = asyncio.get_event_loop()
    state = State(loop)
    if config['general']['run-once']:
        uploader = OneTimeUploader(loop=loop, state=state, config=config)
    else:
        uploader = Uploader(loop=loop, state=state, config=config)
    task = asyncio.ensure_future(uploader.start())
    signal.signal(signal.SIGINT, partial(got_int_signal, state))
    signal.signal(signal.SIGTERM, partial(got_int_signal, state))

    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt as e:
        logger.info("process stopped by keyboard interrupt")
