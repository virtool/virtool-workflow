import asyncio
from concurrent.futures import ThreadPoolExecutor


def asyncio_run(coro, debug=None, n_threads=5):
    """
    Run a coroutine in a new asyncio event loop and ensure that all threads in the default executor have finished.

    `uvloop` (latest release 0.14.0) is not compatible with Python 3.9 as it's event loop does not implement
    `AbstractEventLoop.shutdown_default_executor()`. Using this function instead of `asyncio.run()` maintains
    compatibility by setting the `default_executor` and ensuring it's threads join before the event loop is closed.

    This function is adapted directly from the `asyncio.run()` source code, located at;

    https://github.com/python/cpython/blob/master/Lib/asyncio/runners.py
    """
    if asyncio._get_running_loop() is not None:
        raise RuntimeError(
            "asyncio.run() cannot be called from a running event loop")

    if not asyncio.iscoroutine(coro):
        raise ValueError("a coroutine was expected, got {!r}".format(coro))

    default_executor = ThreadPoolExecutor(n_threads)
    loop = asyncio.new_event_loop()
    loop.set_default_executor(default_executor)
    try:
        asyncio.set_event_loop(loop)
        if debug is not None:
            loop.set_debug(debug)
        return loop.run_until_complete(coro)
    finally:
        try:
            _cancel_all_tasks(loop)
            loop.run_until_complete(loop.shutdown_asyncgens())
            default_executor.shutdown(wait=True)
        finally:
            asyncio.set_event_loop(None)
            loop.close()


def _cancel_all_tasks(loop):
    to_cancel = asyncio.tasks.all_tasks(loop)
    if not to_cancel:
        return

    for task in to_cancel:
        task.cancel()

    loop.run_until_complete(
        asyncio.gather(*to_cancel, loop=loop, return_exceptions=True))

    for task in to_cancel:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler({
                'message': 'unhandled exception during asyncio.run() shutdown',
                'exception': task.exception(),
                'task': task,
            })