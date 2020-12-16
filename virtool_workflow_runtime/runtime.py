"""Main entrypoint(s) to the Virtool Workflow Runtime."""
import asyncio
import logging
from concurrent import futures
from typing import Dict, Any, Callable, Awaitable

import aioredis

from virtool_workflow import hooks
from virtool_workflow.execution.hooks import on_update, on_workflow_finish
from virtool_workflow.execution.workflow_executor import WorkflowExecution, WorkflowError
from virtool_workflow.workflow import Workflow
from virtool_workflow_runtime.abc.runtime import AbstractRuntime
from virtool_workflow_runtime.config.configuration import redis_connection_string, redis_job_list_name
from virtool_workflow_runtime.fixture_loading import InitializedWorkflowFixtureScope
from ._redis import monitor_cancel, redis_list, connect
from .db import VirtoolDatabase


@hooks.on_load_config
def set_log_level_to_debug(config):
    if config.dev_mode:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


runtime_scope = InitializedWorkflowFixtureScope([
    "virtool_workflow_runtime.config.configuration",
    "virtool_workflow.execution.run_in_executor",
    "virtool_workflow.execution.run_subprocess",
    "virtool_workflow.storage.paths",
    "virtool_workflow.subtractions.subtraction",
    "virtool_workflow.analysis.analysis_info",
    "virtool_workflow.analysis.trimming",
    "virtool_workflow.analysis.read_prep",
    "virtool_workflow.analysis.cache",
])


class DirectDatabaseAccessRuntime(AbstractRuntime):
    """Runtime implementation that uses the database directly."""

    def __init__(self, job_id: str):
        self.job_id = job_id
        self._execution = None
        self._scope_initialized = False

    async def _init_scope(self):
        database: VirtoolDatabase = await self.scope.instantiate(VirtoolDatabase)

        job_document = await database["jobs"].find_one(dict(_id=self.job_id))

        @on_update(until=on_workflow_finish)
        async def send_database_updates(update: str):
            await database.send_update(self.job_id, self.execution, update)

        self.scope["job_id"] = self.job_id
        self.scope["job_document"] = job_document
        self.scope["job_args"] = job_document["args"]

        self._scope_initialized = True

    async def execute(self, workflow: Workflow) -> Dict[str, Any]:
        if not self._scope_initialized:
            await self._init_scope()

        self._execution = WorkflowExecution(workflow, self.scope)
        return await self.execution.execute()

    async def execute_function(self, func: Callable[..., Awaitable[Any]]) -> Any:
        if not self._scope_initialized:
            await self._init_scope()

        return (await self.scope.bind(func))()

    @property
    def scope(self):
        return runtime_scope

    @property
    def execution(self) -> WorkflowExecution:
        return self._execution


async def execute(
        workflow: Workflow,
        runtime: AbstractRuntime,
) -> Dict[str, Any]:
    """
    Execute a workflow as a Virtool Job.

    :param runtime: The `AbstractRuntime` implementation.
    :param workflow: The workflow to be executed.
    :return: A dictionary containing the results from the workflow (the results fixture).
    """

    await hooks.on_load_fixtures.trigger(runtime.scope)
    try:
        result = await runtime.execute(workflow)
        await hooks.on_success.trigger(runtime.scope)

        return result
    except Exception as e:
        if isinstance(e, WorkflowError):
            await hooks.on_failure.trigger(runtime.scope, e)
        else:
            await hooks.on_failure.trigger(runtime.scope, WorkflowError(cause=e, context=runtime.execution, workflow=workflow))

        raise e


async def execute_catching_cancellation(job_id, workflow):
    """Execute while catching `asyncio.CancelledError` and triggering `on_failure` and `on_cancelled` hooks."""
    runtime = DirectDatabaseAccessRuntime(job_id)
    try:
        return await execute(workflow, runtime)
    except (asyncio.CancelledError, futures._base.CancelledError) as error:
        await hooks.on_failure.trigger(runtime.scope, WorkflowError(cause=error, workflow=workflow, context=None))
        raise error


async def execute_while_watching_for_cancellation(job_id: str, workflow: Workflow, redis: aioredis.Redis):
    """Start a task which watches for and handles cancellation while the workflow executes."""
    exec_workflow = asyncio.create_task(execute_catching_cancellation(job_id, workflow))
    watch_for_cancel = asyncio.create_task(monitor_cancel(redis, job_id, exec_workflow))

    result = await exec_workflow

    watch_for_cancel.cancel()

    return result


async def execute_from_redis(workflow: Workflow):
    """Execute jobs from the Redis jobs list."""
    async with connect(redis_connection_string()) as redis:
        async for job_id in redis_list(redis, redis_job_list_name()):
            try:
                yield await execute_while_watching_for_cancellation(job_id, workflow, redis)
            except asyncio.CancelledError:
                continue


