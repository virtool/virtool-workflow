from virtool_workflow.api.job import acquire_job


async def test_can_acqure_job(jobs_api_url):
    await acquire_job()
