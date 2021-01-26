"""Main entrypoint(s) to the Virtool Workflow Runtime."""
from concurrent import futures

import aioredis
import asyncio
import logging
from typing import Dict, Any

from virtool_workflow import hooks
from virtool_workflow.analysis.runtime import AnalysisWorkflowRuntime
from virtool_workflow.data_model import Job, Status
from virtool_workflow.execution.workflow_executor import WorkflowError
from virtool_workflow.workflow import Workflow
from virtool_workflow_runtime.config.configuration import db_connection_string, db_name
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
    "virtool_workflow.analysis.fixtures"
])


class DirectDatabaseAccessRuntime(AnalysisWorkflowRuntime):
    """Runtime implementation that uses the database directly."""

    def __init__(self,
                 database: VirtoolDatabase,
                 job: Job):
        self.db = database
        super(AnalysisWorkflowRuntime, self).__init__(job)

    @staticmethod
    async def create(job_id: str, db_name: str, db_connection_string: str):
        db = VirtoolDatabase(db_name, db_connection_string)
        job_document = await db["jobs"].find_one(dict(_id=job_id))

        statuses = [
            Status(status["error"], status["progress"], status["stage"], status["state"], status["timestamp"])
            for status in job_document["status"]
        ] if "status" in job_document else []

        print(job_document)

        job = Job(
            job_document["_id"],
            args=job_document["args"],
            mem=job_document["mem"],
            proc=job_document["proc"],
            task=job_document["task"],
            status=statuses,
        )

        return DirectDatabaseAccessRuntime(db, job)


async def execute(
        workflow: Workflow,
        runtime: AnalysisWorkflowRuntime,
) -> Dict[str, Any]:
    """
    Execute a workflow as a Virtool Job.

    :param runtime: The `AbstractRuntime` implementation.
    :param workflow: The workflow to be executed.
    :return: A dictionary containing the results from the workflow (the results fixture).
    """

    await hooks.on_load_fixtures.trigger(runtime)
    try:
        result = await runtime.execute(workflow)
        await hooks.on_success.trigger(runtime)

        return result
    except Exception as e:
        if isinstance(e, WorkflowError):
            await hooks.on_failure.trigger(runtime, e)
        else:
            await hooks.on_failure.trigger(runtime, WorkflowError(cause=e, context=None, workflow=workflow))

        raise e


async def execute_catching_cancellation(job_id, workflow):
    """Execute while catching `asyncio.CancelledError` and triggering `on_failure` and `on_cancelled` hooks."""
    runtime = await DirectDatabaseAccessRuntime.create(job_id, db_name(), db_connection_string())
    try:
        return await execute(workflow, runtime)
    except (asyncio.CancelledError, futures._base.CancelledError) as error:
        await hooks.on_failure.trigger(runtime, WorkflowError(cause=error, workflow=workflow, context=None))
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


