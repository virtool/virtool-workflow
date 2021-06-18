from pathlib import Path

from tests.api.mocks.mock_subtraction_routes import TEST_SUBTRACTION_ID
from virtool_workflow.analysis.subtractions import subtractions
from virtool_workflow.api.subtractions import SubtractionProvider
from virtool_workflow.data_model import Subtraction


async def test_subtractions(http, jobs_api_url: str, tmpdir):
    subtraction_provider = SubtractionProvider(TEST_SUBTRACTION_ID, http, jobs_api_url, Path(tmpdir))

    _subtractions = await subtractions([subtraction_provider])

    for subtraction in _subtractions:
        assert isinstance(subtraction, Subtraction)
