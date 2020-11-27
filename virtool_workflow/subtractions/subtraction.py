from dataclasses import dataclass
from typing import Dict, Any, List
from pathlib import Path
from virtool_workflow import fixture
from virtool_workflow.db import db


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
    def from_document(document: Dict[str, Any], data_path: Path):
        name = document["name"]
        nickname = document["nickname"]
        path =
        pass


# noinspection PyTypeChecker
@fixture
async def subtractions(job_args: Dict[str, Any], data_path: Path) -> List[Subtraction]:
    ids = job_args["subtraction_id"]
    if isinstance(ids, str):
        ids = [ids]
    return [Subtraction.from_document(await db.fetch_subtraction_document(id_), data_path) for id_ in ids]
