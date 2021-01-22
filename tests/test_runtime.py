from virtool_workflow.runtime import WorkflowEnvironment
from virtool_workflow.data_model import Job

JOB = Job("1", {}, 10, 3)


async def test_workflow_runtime():
    runtime = WorkflowEnvironment(job=JOB)

    for name, fixture in runtime.available.items():
        print(name, fixture)

    raise

