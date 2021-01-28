from dataclasses import dataclass
from typing import Dict, Any, List
from pathlib import Path
from virtool_workflow import fixture
from virtool_workflow.data_model import Subtraction
from virtool_workflow.abc.data_providers import AbstractSubtractionProvider
from virtool_workflow.storage.utils import copy_paths
from virtool_workflow.execution.run_in_executor import FunctionExecutor


# noinspection PyTypeChecker
@fixture
async def subtractions(job_args: Dict[str, Any],
                       subtraction_data_path: Path,
                       subtraction_path: Path,
                       run_in_executor: FunctionExecutor,
                       database: AbstractDatabase) -> List[Subtraction]:
    """The subtractions to be used for the current job."""
    ids = job_args["subtraction_id"]
    if isinstance(ids, str):
        ids = [ids]

    await copy_paths({subtraction_data_path/id_: subtraction_path/id_ for id_ in ids}.items(), run_in_executor)

    return [Subtraction.from_document(await database.fetch_document_by_id(id_, "subtractions"), subtraction_path) for id_ in ids]
