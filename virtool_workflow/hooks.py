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
Triggered when a job fails to complete.

.. code-block:: python

    @on_failure
    async def perform_on_failure(error: WorkflowError):
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


@on_success
async def _trigger_on_finish_from_on_success(scope):
    await on_finish.trigger(scope)


@on_failure
async def _trigger_on_finish_from_on_failure(_, scope):
    await on_finish.trigger(scope)


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
    if isinstance(error, asyncio.CancelledError) or isinstance(error, futures.CancelledError):
        await on_cancelled.trigger(scope, error)


on_load_fixtures = FixtureHook("on_load_fixtures")
"""
Triggered after runtime fixtures have been added to the #WorkflowFixtureScope, but
before the workflow is executed.

Enables modification or injection of specific fixtures before a workflow is executed.

.. code-block:: python

    @on_load_fixtures
    async def change_fixture_values(fixtures: WorkflowFixtureScope):
        fixtures["some_fixture"] = SOME_VALUE
        await fixtures.get_or_instantiate("name_of_some_other_fixture)
        ...
"""

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

on_load_database = Hook("on_load_database")
"""
Triggered before the job document is loaded from the database.

Allows the database to be initialized with additional data.
"""

use_job = Hook("use_job")
"""
Triggered before the job is loaded from the database.

The return value from this hook will be used as the Job for 
the workflow run.
"""

before_result_upload = FixtureHook("before_result_upload")
"""Triggered after the result is ready to be uploaded, but before it is actually uploaded."""

__all__ = [
    "on_result",
    "on_update",
    "on_error",
    "on_workflow_step",
    "on_success",
    "on_failure",
    "on_finalize",
    "on_workflow_failure",
    "on_workflow_finish",
    "on_finish",
    "on_load_config",
    "on_load_fixtures",
    "before_result_upload",
    "on_cancelled",
    "on_state_change",
]
