from typing import Optional, Dict, Any

from virtool_workflow.execution.run_in_executor import run_in_executor, thread_pool_executor
from virtool_workflow.storage.paths import context_directory
from virtool_workflow.analysis.subtractions.subtraction import subtractions
from virtool_workflow.db.db import DirectAccessDatabase
from virtool_workflow.abc.db import AbstractDatabase

mock_subtraction_base = dict(
    name="foobar",
    nickname="bar",
    count="7",
    gc={"A":0.2, "T":0.2, "C":0.2, "G":0.4}
)

mock_subtractions = {str(i): {**mock_subtraction_base, "id": str(i)} for i in range(5)}

subtraction_data_filenames = [
    "subtraction.fa.gz",
    "reference.1.bt2",
    "reference.3.bt2",
    "reference.2.bt2",
    "reference.4.bt2",
    "reference.rev.1.bt2",
    "reference.rev.2.bt2",
]


class MockDatabase(AbstractDatabase):
    async def fetch_document_by_id(self, id_: str, collection_name: str) -> Optional[Dict[str, Any]]:
        return mock_subtractions[id_]


async def test_subtractions(monkeypatch):

    with context_directory("data/subtractions") as subtraction_data_path:

        for subtraction in mock_subtractions.values():
            current_subtraction_data_path = subtraction_data_path/subtraction["id"]
            current_subtraction_data_path.mkdir()

            for name in subtraction_data_filenames:
                (current_subtraction_data_path/name).touch()

        with context_directory("temp/subtractions") as subtraction_path:

            _subtractions = await subtractions(
                job_args=dict(subtraction_id=[s["id"] for s in mock_subtractions.values()]),
                subtraction_data_path=subtraction_data_path,
                subtraction_path=subtraction_path,
                run_in_executor=run_in_executor(thread_pool_executor()),
                database=MockDatabase()
            )

            assert len(_subtractions) == len(mock_subtractions)

            for subtraction, subtraction_document in zip(_subtractions, mock_subtractions.values()):
                assert subtraction.name == subtraction_document["name"]
                assert subtraction.nickname == subtraction_document["nickname"]
                assert subtraction.path == subtraction_path/subtraction_document["id"]
                assert subtraction.fasta_path == subtraction.path/"subtraction.fa.gz"
                assert subtraction.bowtie2_index_path == f"{subtraction.path}/reference"




