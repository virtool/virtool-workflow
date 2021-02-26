from virtool_workflow.api import jobs
from virtool_workflow.testing import install_as_pytest_fixtures

install_as_pytest_fixtures(globals(), jobs.acquire_job)


async def test_job_can_be_acquired(acquire_job):
    test_job = await acquire_job("test_job")
    assert test_job.key is not None
