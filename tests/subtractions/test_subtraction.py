from pathlib import Path

from tests.api.mocks.mock_subtraction_routes import TEST_SUBTRACTION_ID
from virtool_workflow.analysis.subtractions import subtractions
from virtool_workflow.api.subtractions import SubtractionProvider
from virtool_workflow.data_model.subtractions import WFSubtraction


async def test_subtractions(http, jobs_api_connection_string: str, tmpdir):
    subtraction_provider = SubtractionProvider(
        TEST_SUBTRACTION_ID, http, jobs_api_connection_string, Path(tmpdir)
    )

    _subtractions = await subtractions([subtraction_provider])

    for subtraction in _subtractions:
        assert isinstance(subtraction, WFSubtraction)
