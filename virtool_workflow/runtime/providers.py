from virtool_workflow.api import jobs
from virtool_workflow.api.scope import api_fixtures
from virtool_workflow.config import fixtures as config
from virtool_workflow.fixtures import FixtureGroup

providers = FixtureGroup(config.job_id, jobs.acquire_job, **api_fixtures)


@providers.fixture
async def job(job_id, acquire_job):
    return acquire_job(job_id)
