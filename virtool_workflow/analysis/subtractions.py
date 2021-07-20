from typing import List

from virtool_workflow.data_model import Subtraction
from virtool_workflow.api.subtractions import SubtractionProvider

from fixtures import fixture


@fixture
async def subtractions(
        subtraction_providers: List[SubtractionProvider]
) -> List[Subtraction]:
    """The subtractions to be used for the current job."""
    _subtractions = [await provider for provider in subtraction_providers]

    for provider in subtraction_providers:
        await provider.download()

    return _subtractions
