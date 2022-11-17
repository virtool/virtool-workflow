from pathlib import Path

from aiohttp import ClientSession

from tests.api.mocks.mock_subtraction_routes import TEST_SUBTRACTION_ID
from virtool_workflow.analysis.subtractions import subtractions
from virtool_workflow.api.subtractions import SubtractionProvider
from virtool_workflow.data_model.subtractions import WFSubtraction


async def test_subtractions(
    http: ClientSession, jobs_api_connection_string: str, tmpdir
):
    subtraction_provider = SubtractionProvider(
        TEST_SUBTRACTION_ID, http, jobs_api_connection_string, Path(tmpdir)
    )

    for subtraction in await subtractions([subtraction_provider]):
        assert isinstance(subtraction, WFSubtraction)
