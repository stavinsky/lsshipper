import asyncio
from main_handler import MainHandler
import signal
from functools import partial
import logging


signal_times = 0

logger = logging.getLogger(name="general")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class State:
    def __init__(self, need_shutdown=False):
        self._need_shutdown = need_shutdown

    @property
    def need_shutdown(self):
        return self._need_shutdown

    def shutdown(self):
        self._need_shutdown = True

    def __repr__(self,):
        return "shutdown is{} needed".format(
            "" if self._need_shutdown else " not")


def got_int_signal(state, signum, frame):
    global signal_times
    signal_times += 1
    state.shutdown()
    if signal_times > 1:
        loop.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    state = State()
    shipper = MainHandler(loop=loop, state=state)
    task = asyncio.ensure_future(shipper.start())
    signal.signal(signal.SIGINT, partial(got_int_signal, state))

    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt as e:
        logger.info("process stopped by keyboard interrupt")
