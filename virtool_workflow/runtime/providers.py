import asyncio
from typing import List

from aiohttp import ClientSession
from pyfixtures import fixture

from virtool_workflow.api.analysis import AnalysisProvider
from virtool_workflow.api.hmm import HMMsProvider
from virtool_workflow.api.indexes import IndexProvider
from virtool_workflow.api.samples import SampleProvider
from virtool_workflow.api.subtractions import SubtractionProvider
from virtool_workflow.errors import IllegalJobArguments, MissingJobArgument


@fixture
def analysis_provider(job, http, jobs_api_connection_string) -> AnalysisProvider:
    try:
        return AnalysisProvider(
            job.args["analysis_id"], http, jobs_api_connection_string
        )
    except KeyError:
        raise MissingJobArgument("Missing key `analysis_id`")


@fixture
def hmms_provider(http, jobs_api_connection_string, work_path) -> HMMsProvider:
    return HMMsProvider(http, jobs_api_connection_string, work_path)


@fixture
def index_provider(job, http, jobs_api_connection_string) -> IndexProvider:
    try:
        return IndexProvider(
            job.args["index_id"], job.args["ref_id"], http, jobs_api_connection_string
        )
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
def sample_provider(job, http, jobs_api_connection_string: str) -> SampleProvider:
    try:
        return SampleProvider(job.args["sample_id"], http, jobs_api_connection_string)
    except KeyError:
        raise MissingJobArgument("Missing key `sample_id`")


@fixture
async def subtraction_providers(
    job, http: ClientSession, jobs_api_connection_string: str, work_path
) -> List[SubtractionProvider]:
    try:
        ids = job.args["subtractions"]
    except KeyError:
        # Supports the create_subtraction workflow.
        try:
            ids = [job.args["subtraction_id"]]
        except KeyError:
            raise MissingJobArgument("Missing key `subtractions`, or `subtraction_id`")

    if isinstance(ids, (str, bytes)):
        ids = [ids]

    subtraction_work_path = work_path / "subtractions"

    await asyncio.to_thread(subtraction_work_path.mkdir)

    return [
        SubtractionProvider(
            id_, http, jobs_api_connection_string, subtraction_work_path
        )
        for id_ in ids
    ]
