from dataclasses import dataclass
from typing import Dict, Any, List
from pathlib import Path
from virtool_workflow import fixture
from virtool_workflow.abc.db import AbstractDatabase
from virtool_workflow.storage.utils import copy_paths
from virtool_workflow.execution.run_in_executor import FunctionExecutor


@dataclass
class Subtraction:
    """A dataclass representing a subtraction in Virtool."""
    name: str
    """The scientific name for the subtraction."""
    nickname: str
    """The human readable name for the subtraction."""
    path: Path
    """The Path locating the directory containing the subtraction data."""
    fasta_path: Path
    """The Path locating the compressed FASTA data."""
    bowtie2_index_path: str
    """The prefix of all Paths locating the Bowtie2 index data."""
    count: int
    """The number of chromosomes contained in the subtraction data."""
    gc: Dict[str, float]
    """A dict containing the percentage of occurrence for each nucleotide in the FASTA data."""

    @staticmethod
    def from_document(document: Dict[str, Any], subtraction_path: Path):
        """
        Create a new :class:`Subtraction` object based on the data from the subtractions database document.

        :param document: The subtraction document from the database. It is expected to have;

            * name: The scientific name for the subtraction.
            * nickname: The shortened name for the subtraction.
            * count: The chromosome count of the subtraction.
            * gc: The percentage of occurrence of each nucleotide within the FASTA data of the subtraction.

        :param subtraction_path: The path to subtraction data.
        :return: A `Subtraction` instance representing the subtraction given by the subtraction document.
        """
        path = subtraction_path / document["id"]

        return Subtraction(
            name=document["name"],
            nickname=document["nickname"],
            path=path,
            fasta_path=path / "subtraction.fa.gz",
            bowtie2_index_path=f"{path}/reference",
            count=document["count"],
            gc=document["gc"]
        )


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
