from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import suppress

import pytest

from virtool_workflow import hooks
import virtool_workflow.execution.run_subprocess
import virtool_workflow.execution.run_in_executor


@pytest.fixture
def run_in_executor():
    return virtool_workflow.execution.run_in_executor.run_in_executor(
        ThreadPoolExecutor()
    )


@pytest.fixture
def run_subprocess():
    return virtool_workflow.execution.run_subprocess.run_subprocess()


@pytest.fixture
def clear_hooks():
    """Temporarily clear hooks for a test."""
    backups = {}
    try:
        for hook in vars(hooks).values():
            if isinstance(hook, hooks.Hook):
                backups[hook] = hook.callbacks
                hook.callbacks = []
        yield
    finally:
        for hook, callbacks in backups.items():
            hook.callbacks = callbacks
        


