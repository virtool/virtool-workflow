from typing import List

from virtool_workflow.abc.data_providers import AbstractSubtractionProvider
from virtool_workflow.data_model import Subtraction

from fixtures import fixture


# noinspection PyTypeChecker
@fixture
async def subtractions(
        subtraction_providers: List[AbstractSubtractionProvider]
) -> List[Subtraction]:
    """The subtractions to be used for the current job."""
    _subtractions = [await provider for provider in subtraction_providers]

    for provider in subtraction_providers:
        await provider.download()

    return _subtractions
