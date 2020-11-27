from dataclasses import dataclass
from typing import Dict, Any, List
from pathlib import Path
from virtool_workflow import fixture
from virtool_workflow.db import db
from virtool_workflow.storage.utils import copy_paths
from virtool_workflow.execute import FunctionExecutor


@dataclass
class Subtraction:
    name: str
    nickname: str
    path: Path
    fasta_path: Path
    bowtie2_index_path: str
    sequence_count: int
    gc: Dict[str, float]

    @staticmethod
    def from_document(document: Dict[str, Any], subtraction_path: Path):
        path = subtraction_path / document["id"]

        return Subtraction(
            name=document["name"],
            nickname=document["nickname"],
            path=path,
            fasta_path=path / "subtraction.fa.gz",
            bowtie2_index_path=f"{path}/reference",
            sequence_count=document["count"],
            gc=document["gc"]
        )


# noinspection PyTypeChecker
@fixture
async def subtractions(job_args: Dict[str, Any],
                       subtraction_data_path: Path,
                       subtraction_path: Path,
                       run_in_executor: FunctionExecutor) -> List[Subtraction]:
    """The subtractions to be used for the current job."""
    ids = job_args["subtraction_id"]
    if isinstance(ids, str):
        ids = [ids]

    await copy_paths({subtraction_data_path/id_: subtraction_path/id_ for id_ in ids}, run_in_executor)

    return [Subtraction.from_document(await db.fetch_subtraction_document(id_), subtraction_data_path) for id_ in ids]
