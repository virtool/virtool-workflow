from virtool_workflow.api import jobs
from virtool_workflow.data_model import Status
from virtool_workflow.testing import install_as_pytest_fixtures

install_as_pytest_fixtures(globals(), jobs.acquire_job)


async def test_job_can_be_acquired(acquire_job):
    test_job = await acquire_job("test_job")
    assert test_job.key is not None


async def test_push_status(acquire_job, http, jobs_api_url: str):
    job = await acquire_job("test_job")
    push_status = jobs.push_status(job, http, jobs_api_url)
    status = await push_status("running", "test_stage", 40, None)

    assert isinstance(status, Status)
