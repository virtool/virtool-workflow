from importlib import import_module

import pytest

from virtool_workflow import hooks
from virtool_workflow.runtime.hook import Hook

import_module("virtool_workflow.data")




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
