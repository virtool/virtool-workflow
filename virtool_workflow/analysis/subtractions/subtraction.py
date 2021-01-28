from pathlib import Path
from typing import List

from virtool_workflow import fixture
from virtool_workflow.abc.data_providers import AbstractSubtractionProvider
from virtool_workflow.data_model import Subtraction
from virtool_workflow.execution.run_in_executor import FunctionExecutor
from virtool_workflow.storage.utils import copy_paths


# noinspection PyTypeChecker
@fixture
async def subtractions(subtraction_data_path: Path,
                       subtraction_path: Path,
                       run_in_executor: FunctionExecutor,
                       subtraction_providers: List[AbstractSubtractionProvider]
                       ) -> List[Subtraction]:
    """The subtractions to be used for the current job."""
    _subtractions = [provider.fetch_subtraction(subtraction_path) for provider in subtraction_providers]

    await copy_paths({subtraction_data_path / subtraction.id: subtraction_path / subtraction.id
                      for subtraction in _subtractions}.items(), run_in_executor)

    return _subtractions
