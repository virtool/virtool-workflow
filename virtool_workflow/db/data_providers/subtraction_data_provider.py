from virtool_workflow.abc.data_providers import AbstractSubtractionProvider
from virtool_workflow.abc.db import AbstractDatabaseCollection
from virtool_workflow.data_model import Subtraction, NucleotideComposition


class SubtractionDataProvider(AbstractSubtractionProvider):

    def __init__(self, subtraction_id: str, subtractions: AbstractDatabaseCollection):
        self.subtraction_id = subtraction_id
        self.subtractions = subtractions

    async def fetch_subtraction(self, subtraction_path) -> Subtraction:
        subtraction = await self.subtractions.get(self.subtraction_id)

        return Subtraction(
            id=subtraction["id"],
            name=subtraction["name"],
            nickname=subtraction["nickname"],
            count=subtraction["count"],
            gc=subtraction["gc"],
            is_host=subtraction["is_host"],
            deleted=subtraction_path["deleted"],
            path=subtraction_path,
            fasta_path=subtraction_path / "subtraction.fa.gz",
            bowtie2_index_path=f"{subtraction_path}/reference"
        )

    async def store_count_and_gc(self, count: int, gc: NucleotideComposition):
        await self.subtractions.set(self.subtraction_id, count=count, gc=gc)

    async def delete(self):
        await self.subtractions.delete(self.subtraction_id)
