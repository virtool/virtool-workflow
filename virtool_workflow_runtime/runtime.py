from virtool_workflow import Workflow
from virtool_workflow.workflow_fixture import WorkflowFixtureScope
import virtool_workflow.execute_workflow
from .job import Job
from .db import VirtoolDatabase, DEFAULT_DATABASE_NAME


async def execute(workflow: Workflow, job_id: str, database_name: str = DEFAULT_DATABASE_NAME):
    scope = WorkflowFixtureScope()

    job = Job(job_id, workflow)

    db: VirtoolDatabase = scope.instantiate(VirtoolDatabase)
    db.set_updates_for_job(job)

    return await virtool_workflow.execute_workflow.execute(job.workflow, _context=job.context, scope=scope)

