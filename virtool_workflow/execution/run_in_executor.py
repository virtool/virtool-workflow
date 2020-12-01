"""Helper functions for threading and running subprocesses within Virtool Workflows."""
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, Coroutine

from virtool_workflow.fixtures.workflow_fixture import fixture


@fixture
def thread_pool_executor() -> ThreadPoolExecutor:
    """A fixture for a #concurrent.futures.ThreadPoolExecutor to be used by #run_in_executor()."""
    return ThreadPoolExecutor()


FunctionExecutor = Callable[..., Coroutine[Any, Any, Any]]


@fixture
def run_in_executor(thread_pool_executor: ThreadPoolExecutor) -> FunctionExecutor:
    """
    Fixture to execute functions in a #concurrent.futures.ThreadPoolExecutor.

    Wraps #concurrent.futures.ThreadPoolExecutor.submit() as an async function.
    """
    async def _run_in_executor(func, *args, **kwargs):
        future = thread_pool_executor.submit(func, *args, **kwargs)
        return future.result()

    return _run_in_executor
