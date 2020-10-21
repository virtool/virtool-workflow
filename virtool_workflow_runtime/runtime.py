import virtool_workflow.execute_workflow
from virtool_workflow import Workflow
from virtool_workflow.workflow_fixture import WorkflowFixtureScope
from ._redis import job_id_queue
from .db import VirtoolDatabase
from .job import Job


async def execute(workflow: Workflow, job_id: str):
    scope = WorkflowFixtureScope()

    job = Job(job_id, workflow)

    db: VirtoolDatabase = await scope.instantiate(VirtoolDatabase)
    db.send_updates_to_database_for_job(job)

    job_document = await db["jobs"].find_one(dict(_id=job_id))

    scope["job_id"] = job_id
    scope["job_document"] = job_document

    return await virtool_workflow.execute_workflow.execute(
        _wf=job.workflow,
        _context=job.context,
        scope=scope)


async def execute_from_redis(workflow: Workflow):
    async for job_id in job_id_queue():
        yield await execute(workflow, job_id)



