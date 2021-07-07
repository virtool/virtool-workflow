"""
Hooks provide a way to do things when events happen during the workflow lifecycle.

"""

from concurrent import futures

import asyncio

from virtool_workflow.execution.hooks.fixture_hooks import FixtureHook
from virtool_workflow.execution.hooks.hooks import Hook
from virtool_workflow.execution.hooks.workflow_hooks import *

on_success = FixtureHook("on_success")
"""
Triggered when a job completes successfully.

Parameters supplied are the `Workflow` instance and the results dict.

.. code-block:: python

    @on_success
    async def perform_on_success(workflow: Workflow, results: Dict[str, Any]):
        ...
"""

on_failure = FixtureHook("on_failure")
"""
Triggered when a job fails to complete. The exception
which caused the failure will be found in the `error` fixture.

.. code-block:: python

    @on_failure
    async def perform_on_failure(error: Exception):
        ...
"""

on_finish = FixtureHook("on_finish")
"""
Triggered when a job finishes, regardless of success or failure.

.. code-block:: python

    @on_finish
    async def perform_on_finish(workflow: Workflow):
        ...
"""


on_finalize = FixtureHook("on_finalize")
"""
Triggered after job finishes, regardless of success or failure.

Intended for finalization actions such as closing the fixture scope.
"""


on_cancelled = FixtureHook("on_cancelled")
"""
Triggered when a job is cancelled.

.. code-block:: python

    @on_cancelled
    async def on_cancelled(error: asyncio.CancelledError):
        ...
"""


@on_failure
async def _trigger_on_cancelled(error: Exception, scope):
    if (isinstance(error, asyncio.CancelledError)
            or isinstance(error, futures.CancelledError)):
        await on_cancelled.trigger(scope, error)


on_load_config = FixtureHook("on_load_config")
"""
Triggered after the config is loaded from the CLI arguments and environment variables. A SimpleNamespace object
is provided which has an attribute (sharing the same name as the fixture) for each configuration fixture in
:mod:`virtool_workflow_runtime.config.configuration`. 

.. code-block:: python

    @on_load_config
    def use_config(dev_mode):
        if dev_mode:
            ...
"""

before_result_upload = FixtureHook("before_result_upload")
"""Triggered after the result is ready to be uploaded, but before it is actually uploaded."""

__all__ = [
    "on_result",
    "on_update",
    "on_success",
    "on_failure",
    "on_finalize",
    "on_finish",
    "on_load_config",
    "before_result_upload",
    "on_cancelled",
]
