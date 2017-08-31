import asyncio
from main_handler import MainHandler
import signal

signal_times = 0


def got_int_signal(signum, frame):
    global signal_times
    signal_times += 1
    print('we are in signal')
    shipper.stop_now = True
    if signal_times > 1:
        loop.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    shipper = MainHandler(loop=loop)
    task = asyncio.ensure_future(shipper.start())
    signal.signal(signal.SIGINT, got_int_signal)

    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt as e:
        print(e)
        shipper.stop_now = True
    finally:
        pass
        # print("we got 'finally'")
        # pending = asyncio.Task.all_tasks()
        # for p in pending:
        #     print(p)
        # loop.run_until_complete(asyncio.gather(*pending))
        # loop.run_until_complete(task)
        # loop.close()
