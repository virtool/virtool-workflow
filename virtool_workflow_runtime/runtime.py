"""Main entrypoint(s) to the Virtool Workflow Runtime."""
import asyncio
from typing import Dict, Any

from virtool_workflow.execution.hooks import on_update, on_workflow_finish
from virtool_workflow.execution.workflow_executor import WorkflowExecution, WorkflowError
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from virtool_workflow.workflow import Workflow
from . import hooks
from ._redis import job_id_queue, monitor_cancel
from .db import VirtoolDatabase
from virtool_workflow_runtime.config.environment import redis_connection_string


async def execute(job_id: str, workflow: Workflow) -> Dict[str, Any]:
    """
    Execute a workflow as a Virtool Job.

    :param job_id: The id of the job in the Virtool jobs database.
    :param workflow: The workflow to be executed
    :return: A dictionary containing the results from the workflow (the results fixture).
    """

    with WorkflowFixtureScope() as fixtures:
        executor = WorkflowExecution(workflow, fixtures)
        try:
            result = await _execute(job_id, workflow, fixtures, executor)

            await hooks.on_success.trigger(workflow, result)

            return result
        except Exception as e:
            if isinstance(e, WorkflowError):
                await hooks.on_failure.trigger(e)
            else:
                await hooks.on_failure.trigger(WorkflowError(cause=e, context=executor, workflow=workflow))

            raise e


async def _execute(job_id: str,
                   workflow: Workflow,
                   fixtures: WorkflowFixtureScope,
                   executor: WorkflowExecution) -> Dict[str, Any]:

    await hooks.on_load_fixtures.trigger(fixtures)

    database: VirtoolDatabase = await fixtures.instantiate(VirtoolDatabase)

    job_document = await database["jobs"].find_one(dict(_id=job_id))

    executor = WorkflowExecution(workflow, fixtures)

    @on_update(until=on_workflow_finish)
    async def send_database_updates(_, update: str):
        await database.send_update(job_id, executor, update)

    fixtures["job_id"] = job_id
    fixtures["job_document"] = job_document

    return await executor


on_cancelled = hooks.Hook("on_cancelled", [Workflow, asyncio.CancelledError], None)


async def execute_catching_cancellation(job_id, workflow):
    try:
        with WorkflowFixtureScope() as fixtures:
            execution = WorkflowExecution(workflow, fixtures)
            return await execution
    except asyncio.CancelledError as error:
        await hooks.on_failure.trigger(WorkflowError(cause=error, workflow=workflow, context=execution))
        await on_cancelled.trigger(workflow, error)
        raise error


async def execute_while_watching_for_cancellation(job_id: str, workflow: Workflow):
    exec_workflow = asyncio.create_task(execute_catching_cancellation(job_id, workflow))
    watch_for_cancel = asyncio.create_task(monitor_cancel(redis_connection_string(), job_id, exec_workflow))

    result = await exec_workflow

    watch_for_cancel.cancel()

    return result


async def execute_from_redis(workflow: Workflow):
    """Execute jobs from the Redis jobs list."""
    async for job_id in job_id_queue(redis_connection_string()):
        try:
            yield await execute_while_watching_for_cancellation(job_id, workflow)
        except asyncio.CancelledError:
            continue


