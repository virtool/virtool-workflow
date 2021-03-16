from virtool_workflow.api import jobs
from virtool_workflow.api.analysis import AnalysisProvider
from virtool_workflow.api.hmm import HMMsProvider
from virtool_workflow.api.indexes import IndexProvider
from virtool_workflow.api.scope import api_fixtures
from virtool_workflow.config import fixtures as config
from virtool_workflow.fixtures import FixtureGroup

providers = FixtureGroup(config.job_id, jobs.acquire_job, **api_fixtures)


@providers.fixture
async def _job(job_id, acquire_job):
    return acquire_job(job_id)


@providers.fixture
def analysis_provider(job, http, jobs_api_url):
    return AnalysisProvider(job.args["analysis_id"], http, jobs_api_url)


@providers.fixture
def hmms_provider(http, jobs_api_url, work_path):
    return HMMsProvider(http, jobs_api_url, work_path)


@providers.fixture
def index_provider(job, http, jobs_api_url):
    return IndexProvider(job.args["index_id"], job.args["ref_id"], http, jobs_api_url)
