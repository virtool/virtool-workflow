"""Main entrypoint(s) to the Virtool Workflow Runtime."""
from typing import Dict, Any

import virtool_workflow.execute_workflow
from virtool_workflow import Workflow, WorkflowExecutionContext
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from ._redis import job_id_queue
from .db import VirtoolDatabase


async def execute(job_id: str, workflow: Workflow,
                  context: WorkflowExecutionContext = None) -> Dict[str, Any]:
    """
    Execute a workflow as a Virtool Job.

    :param job_id: The id of the job in the Virtool jobs database.
    :param workflow: The workflow to be executed
    :param context: The initialized WorkflowExecutionContext. If none
        is provided a new :class:`WorkflowExecutionContext` will be created.
    :return: A dictionary containing the results from the workflow (the results fixture).
    """
    if not context:
        context = WorkflowExecutionContext()

    scope = WorkflowFixtureScope()

    database: VirtoolDatabase = await scope.instantiate(VirtoolDatabase)
    database.send_updates_to_database_for_job(job_id, context, workflow)

    job_document = await database["jobs"].find_one(dict(_id=job_id))

    scope["job_id"] = job_id
    scope["job_document"] = job_document

    return await virtool_workflow.execute_workflow.execute(
        _wf=workflow,
        _context=context,
        scope=scope)


async def execute_from_redis(workflow: Workflow):
    """Execute jobs from the Redis jobs list."""
    async for job_id in job_id_queue():
        yield await execute(job_id, workflow)
