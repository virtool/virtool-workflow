from typing import List

from pyfixtures import fixture

from virtool_workflow.api.subtractions import SubtractionProvider
from virtool_workflow.data_model.subtractions import WFSubtraction


@fixture
async def subtractions(
    subtraction_providers: List[SubtractionProvider],
) -> List[WFSubtraction]:
    """The subtractions to be used for the current job."""
    _subtractions = [await provider.get() for provider in subtraction_providers]

    for provider in subtraction_providers:
        await provider.download()

    return _subtractions
