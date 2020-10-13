from virtool_workflow import Workflow
from virtool_workflow.workflow_fixture import WorkflowFixtureScope
import virtool_workflow.execute_workflow
from .job import Job
from .db import VirtoolDatabase


async def execute_with_initialization(workflow: Workflow, job_id: str):
    """
    Execute a workflow and access the :class:`Job` and :class:`WorkflowFixtureScope`
    objects before the workflow starts.

    :param workflow:
    :param job_id:
    :yields: First a Tuple[Job, WorkflowFixtureScope], then a Dict[str, Any] (the workflow result)
    """
    scope = WorkflowFixtureScope()

    job = Job(job_id, workflow)

    db: VirtoolDatabase = scope.instantiate(VirtoolDatabase)
    db.set_updates_for_job(job)

    yield job, scope
    yield await virtool_workflow.execute_workflow.execute(job.workflow, _context=job.context, scope=scope)


async def execute(workflow: Workflow, job_id: str):
    async for _ in execute_with_initialization(workflow, job_id):
        pass



