from numbers import Number

from typing import Optional, Dict, Any

from virtool_workflow.analysis.subtractions.subtraction import subtractions
from virtool_workflow.abc.data_providers import AbstractSubtractionProvider
from virtool_workflow.data_model import Subtraction, NucleotideComposition

mock_subtractions = {str(i): {"id": str(i)} for i in range(5)}

subtraction_data_filenames = [
    "subtraction.fa.gz",
    "reference.1.bt2",
    "reference.3.bt2",
    "reference.2.bt2",
    "reference.4.bt2",
    "reference.rev.1.bt2",
    "reference.rev.2.bt2",
]


class TestSubtractionProvider(AbstractSubtractionProvider):

    def __init__(self, _id: str):
        self.id = _id

    async def fetch_subtraction(self, subtraction_path) -> Subtraction:
        return Subtraction(
            id=self.id,
            name="foobar",
            nickname="bar",
            count=7,
            is_host=False,
            deleted=False,
            path=subtraction_path,
            fasta_path=subtraction_path / "subtraction.fa.gz",
            bowtie2_index_path=f"{subtraction_path}/reference",
            gc=NucleotideComposition(a=0.2, t=0.2, c=0.2, g=0.4, n=0.0),
        )

    async def store_count_and_gc(self, count: int, gc: Dict[str, Number]):
        pass

    async def delete(self):
        pass


async def setup_sample_data_path(runtime):
    subtraction_path = await runtime.get_or_instantiate("subtraction_data_path")

    for subtraction in mock_subtractions.values():
        current_subtraction_data_path = subtraction_path / subtraction["id"]
        current_subtraction_data_path.mkdir()

        for name in subtraction_data_filenames:
            (current_subtraction_data_path / name).touch()


async def test_subtractions(monkeypatch, runtime):
    runtime.data_providers.subtraction_providers = [TestSubtractionProvider(id_) for id_ in mock_subtractions]

    await setup_sample_data_path(runtime)
    _subtractions = await runtime.instantiate(subtractions)

    assert len(_subtractions) == len(mock_subtractions)

    for subtraction, subtraction_document in zip(_subtractions, mock_subtractions.values()):
        assert subtraction.name == subtraction_document["name"]
        assert subtraction.nickname == subtraction_document["nickname"]
        assert subtraction.path == runtime["subtraction_path"] / \
            subtraction_document["id"]
        assert subtraction.fasta_path == subtraction.path/"subtraction.fa.gz"
        assert subtraction.bowtie2_index_path == f"{subtraction.path}/reference"
