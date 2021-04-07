from typing import List

from virtool_workflow.api import jobs
from virtool_workflow.api.analysis import AnalysisProvider
from virtool_workflow.api.hmm import HMMsProvider
from virtool_workflow.api.indexes import IndexProvider
from virtool_workflow.api.samples import SampleProvider
from virtool_workflow.api.scope import api_fixtures
from virtool_workflow.api.subtractions import SubtractionProvider
from virtool_workflow.config import fixtures as config
from virtool_workflow.data_model import Job
from virtool_workflow.fixtures import FixtureGroup

providers = FixtureGroup(
    config.job_id, jobs.acquire_job, jobs.push_status, **api_fixtures
)
"""A :class:`FixtureGroup` containing all data provider fixtures."""


@providers.fixture
async def _job(job_id, acquire_job) -> Job:
    return await acquire_job(job_id)


@providers.fixture
def analysis_provider(job, http, jobs_api_url) -> AnalysisProvider:
    return AnalysisProvider(job.args["analysis_id"], http, jobs_api_url)


@providers.fixture
def hmms_provider(http, jobs_api_url, work_path) -> HMMsProvider:
    return HMMsProvider(http, jobs_api_url, work_path)


@providers.fixture
def index_provider(job, http, jobs_api_url) -> IndexProvider:
    return IndexProvider(job.args["index_id"], job.args["ref_id"], http, jobs_api_url)


@providers.fixture
def sample_provider(job, http, jobs_api_url) -> SampleProvider:
    return SampleProvider(job.args["sample_id"], http, jobs_api_url)


@providers.fixture
def subtraction_providers(
    job, http, jobs_api_url, work_path
) -> List[SubtractionProvider]:
    ids = job.args["subtraction_id"]
    if isinstance(ids, str) or isinstance(ids, bytes):
        ids = [ids]

    subtraction_work_path = work_path / "subtractions"
    subtraction_work_path.mkdir()

    return [
        SubtractionProvider(id_, http, jobs_api_url, subtraction_work_path)
        for id_ in ids
    ]
