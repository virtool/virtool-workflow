from pytest import fixture

from virtool_workflow.api import jobs


@fixture
def mem():
    return 8


@fixture
def proc():
    return 4


async def test_job_can_be_acquired(http, jobs_api_connection_string, mem, proc):
    test_job = await jobs.acquire_job(http, jobs_api_connection_string, mem, proc)(
        "test_job"
    )
    assert test_job.key is not None
