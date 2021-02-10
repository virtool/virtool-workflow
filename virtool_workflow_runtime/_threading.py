import asyncio
from threading import Thread


def run_async_function_in_thread(coroutine, daemon=True) -> Thread:
    """
    Start a new thread with a running asyncio event loop.

    This allows work to be submitted to the new thread using :func:`loop.call_soon_threadsafe`.

    :param coroutine: The async function to run.
    :param daemon: A flag indicating that the thread is a daemon thread and should be killed when the
        program exits.

    :return: The :class:`Threading.Thread` object and the :class:`asyncio.AbstractEventLoop` object.
    """
    thread = Thread(target=asyncio.run, args=(coroutine,))
    thread.daemon = daemon
    thread.start()

    return thread
