from integration_test_workflows import samples_workflow
from virtool_workflow.decorator_api import collect


async def test_samples(runtime, docker_jobs_api):
    runtime["jobs_api_url"] = docker_jobs_api
    workflow = collect(samples_workflow)
    await runtime.execute(workflow)
