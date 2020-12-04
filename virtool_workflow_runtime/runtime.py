"""Main entrypoint(s) to the Virtool Workflow Runtime."""
import logging
import asyncio
import aioredis
from typing import Dict, Any
from concurrent import futures

from virtool_workflow.execution.hooks import on_update, on_workflow_finish, on_load_config
from virtool_workflow.execution.workflow_executor import WorkflowExecution, WorkflowError
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from virtool_workflow.workflow import Workflow
from virtool_workflow import hooks
from ._redis import monitor_cancel, redis_list, connect
from .db import VirtoolDatabase
from virtool_workflow_runtime.config.configuration import redis_connection_string, redis_job_list_name

logger = logging.getLogger(__name__)


@on_load_config
def set_log_level_to_debug(config):
    if config.dev_mode:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


async def execute(
        job_id: str,
        workflow: Workflow,
        scope: WorkflowFixtureScope,
) -> Dict[str, Any]:
    """
    Execute a workflow as a Virtool Job.

    :param job_id: The id of the job in the Virtool jobs database.
    :param workflow: The workflow to be executed.
    :param scope: The WorkflowFixtureScope to use.
    :return: A dictionary containing the results from the workflow (the results fixture).
    """

    logger.debug("Creating a new WorkflowExecution")
    executor = WorkflowExecution(workflow, fixtures)
    try:
        result = await _execute(job_id, workflow, fixtures, executor)
        await hooks.on_success.trigger(workflow, result)

        return result
    except Exception as e:
        if isinstance(e, WorkflowError):
            await hooks.on_failure.trigger(scope, e)
        else:
            await hooks.on_failure.trigger(scope, WorkflowError(cause=e, context=executor, workflow=workflow))

        raise e


async def _execute(job_id: str,
                   workflow: Workflow,
                   fixtures: WorkflowFixtureScope,
                   executor: WorkflowExecution) -> Dict[str, Any]:

    await hooks.on_load_fixtures.trigger(fixtures)

    database: VirtoolDatabase = await fixtures.instantiate(VirtoolDatabase)

    logger.info("Fetching job document.")
    job_document = await database["jobs"].find_one(dict(_id=job_id))

    executor = WorkflowExecution(workflow, fixtures)

    @on_update(until=on_workflow_finish)
    async def send_database_updates(update: str):
        await database.send_update(job_id, executor, update)

    fixtures["job_id"] = job_id
    fixtures["job_document"] = job_document
    fixtures["job_args"] = job_document["args"]

    return await executor


async def execute_catching_cancellation(job_id, workflow):
    """Execute while catching `asyncio.CancelledError` and triggering `on_failure` and `on_cancelled` hooks."""
    with WorkflowFixtureScope() as scope:
        try:
            return await execute(job_id, workflow, scope)
        except (asyncio.CancelledError, futures._base.CancelledError) as error:
            await hooks.on_failure.trigger(scope, WorkflowError(cause=error, workflow=workflow, context=None))
            raise error


async def execute_while_watching_for_cancellation(job_id: str, workflow: Workflow,
                                                  redis: aioredis.Redis):
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


