from concurrent.futures.thread import ThreadPoolExecutor

import pytest

import virtool_workflow.execution.run_in_executor
import virtool_workflow.execution.run_subprocess
from virtool_workflow import hooks
from virtool_workflow.execution.hooks import Hook


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
            if isinstance(hook, Hook):
                backups[hook] = hook.callbacks
                hook.callbacks = []
        yield
    finally:
        for hook, callbacks in backups.items():
            hook.callbacks = callbacks
