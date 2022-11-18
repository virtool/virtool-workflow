from virtool_workflow.api import jobs


async def test_job_can_be_acquired(http, jobs_api_connection_string):
    test_job = await jobs.acquire_job(http, jobs_api_connection_string)("test_job")
    assert test_job.key is not None
