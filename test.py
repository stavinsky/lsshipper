import asyncio
shutdown = False

async def test_func():
    while not shutdown:
        print("test")
        await asyncio.sleep(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(test_func(), loop=loop)

    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        shutdown = True
