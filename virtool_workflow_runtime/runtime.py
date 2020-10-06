from virtool_workflow import Workflow
import virtool_workflow.execute_workflow
from .job import Job
from .db import set_database_updates, connect, DATABASE_NAME


async def execute(workflow: Workflow, job_id: str, database_name: str = DATABASE_NAME):
    job = Job(job_id, workflow)
    set_database_updates(job, connect(database_name))
    return await virtool_workflow.execute_workflow.execute(job.workflow, context=job.context)

