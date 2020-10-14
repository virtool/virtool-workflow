from copy import copy
from virtool_workflow import Workflow
from virtool_workflow.workflow_fixture import WorkflowFixtureScope
import virtool_workflow.execute_workflow
from .job import Job
from .db import VirtoolDatabase
from ._redis import job_id_queue


async def execute(workflow: Workflow, job_id: str):
    scope = WorkflowFixtureScope()

    job = Job(job_id, workflow)

    db: VirtoolDatabase = scope.instantiate(VirtoolDatabase)
    db.send_updates_to_database_for_job(job)

    return await virtool_workflow.execute_workflow.execute(
        _wf=job.workflow,
        _context=job.context,
        scope=scope)


async def execute_from_redis(workflow: Workflow):
    async for job_id in job_id_queue():
        yield await execute(workflow, job_id)



