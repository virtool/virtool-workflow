"""Helper functions for threading and running subprocesses within Virtool Workflows."""
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Coroutine, Protocol, runtime_checkable

from fixtures import fixture


@fixture
def thread_pool_executor() -> ThreadPoolExecutor:
    """A fixture for a :class:`concurrent.futures.ThreadPoolExecutor` to be used by :func:`run_in_executor`."""
    return ThreadPoolExecutor()


@runtime_checkable
class FunctionExecutor(Protocol):
    def __call__(self, func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Coroutine:
        ...


@fixture
def run_in_executor(thread_pool_executor: ThreadPoolExecutor) -> FunctionExecutor:
    """
    Fixture to execute functions in a #concurrent.futures.ThreadPoolExecutor.

    Wraps :func:`concurrent.futures.ThreadPoolExecutor.submit()` as an async function.
    """
    async def _run_in_executor(func: Callable, *args, **kwargs):
        future = thread_pool_executor.submit(func, *args, **kwargs)
        return future.result()

    return _run_in_executor
