from typing import List

from fixtures import fixture
from virtool_workflow.api.analysis import AnalysisProvider
from virtool_workflow.api.hmm import HMMsProvider
from virtool_workflow.api.indexes import IndexProvider
from virtool_workflow.api.samples import SampleProvider
from virtool_workflow.api.subtractions import SubtractionProvider
from virtool_workflow.errors import IllegalJobArguments, MissingJobArgument


@fixture
def analysis_provider(job, http, jobs_api_url) -> AnalysisProvider:
    return AnalysisProvider(job.args["analysis_id"], http, jobs_api_url)


@fixture
def hmms_provider(http, jobs_api_url, work_path) -> HMMsProvider:
    return HMMsProvider(http, jobs_api_url, work_path)


@fixture
def index_provider(job, http, jobs_api_url) -> IndexProvider:
    try:
        return IndexProvider(job.args["index_id"], job.args["ref_id"], http, jobs_api_url)
    except KeyError as e:
        key = e.args[0]

        if key == "ref_id":
            raise IllegalJobArguments(
                f"Index {job.args['index_id']} given without 'ref_id'."
            )

        if key == "index_id":
            raise MissingJobArgument("Missing key 'index_id'")

        raise


@fixture
def sample_provider(job, http, jobs_api_url) -> SampleProvider:
    return SampleProvider(job.args["sample_id"], http, jobs_api_url)


@fixture
def subtraction_providers(
    job, http, jobs_api_url, work_path
) -> List[SubtractionProvider]:
    try:
        ids = job.args["subtractions"]
    except KeyError:
        # Supports the create_subtraction workflow.
        ids = [job.args["subtraction_id"]]

    if isinstance(ids, str) or isinstance(ids, bytes):
        ids = [ids]

    subtraction_work_path = work_path / "subtractions"
    subtraction_work_path.mkdir()

    return [
        SubtractionProvider(id_, http, jobs_api_url, subtraction_work_path)
        for id_ in ids
    ]
