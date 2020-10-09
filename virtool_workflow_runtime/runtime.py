from virtool_workflow import Workflow
from virtool_workflow.workflow_fixture import WorkflowFixtureScope
import virtool_workflow.execute_workflow
from .job import Job
from .db import set_database_updates, connect, DATABASE_NAME


async def execute(workflow: Workflow, job_id: str, database_name: str = DATABASE_NAME):
    job = Job(job_id, workflow)
    db = connect(database_name)
    set_database_updates(job, db)

    scope = WorkflowFixtureScope()
    scope.add_instance(db, "db", "database", "mongo")
    return await virtool_workflow.execute_workflow.execute(job.workflow, _context=job.context, scope=scope)

