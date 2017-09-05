from lsshipper.common.config import prepare_config
import asyncio
from .file_handler import FileHandler
import signal
from functools import partial
import logging
import logging.config
from .common.state import State

signal_times = 0
logger = logging.getLogger('general')


def got_int_signal(state, signum, frame):
    global signal_times
    signal_times += 1
    state.shutdown()
    if signal_times > 1:
        state.loop.close()


def main():
    config = prepare_config()
    loop = asyncio.get_event_loop()
    state = State(loop)
    shipper = FileHandler(loop=loop, state=state, config=config)
    if config['general']['run-once']:
        task = asyncio.ensure_future(shipper.run_once())
    else:
        task = asyncio.ensure_future(shipper.start())

    signal.signal(signal.SIGINT, partial(got_int_signal, state))

    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt as e:
        logger.info("process stopped by keyboard interrupt")
