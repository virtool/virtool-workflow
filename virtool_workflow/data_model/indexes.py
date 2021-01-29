from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict
from virtool_workflow.data_model.references import Reference


@dataclass
class Index(ABC):
    id: str
    path: Path
    reference: Reference

    @abstractmethod
    async def decompress_json(self, processes: int):
        """
        Decompress the gzipped JSON file stored in the reference index directory.

        This data will be used to generate isolate indexes if required and the
        ``sequence_otu_map`` attribute will be populated.

        :param processes: the number processes available for decompression
        """
        ...

    @abstractmethod
    def get_otu_id_by_sequence_id(self, sequence_id: str) -> str:
        """
        Return the OTU ID associated with the given ``sequence_id``.

        :param sequence_id: the sequence ID
        :return: the matching OTU ID
        """
        ...

    @abstractmethod
    def write_isolate_fasta(self, otu_ids: List[str], path: Path):
        """
        Generate a FASTA file for all of the isolates of the OTUs specified by ``otu_ids``.

        :param otu_ids: the list of OTU IDs for which to generate and index
        :param path: the path to the reference index directory
        :return: a dictionary of the lengths of all sequences keyed by their IDS
        """

    @abstractmethod
    async def build_isolate_index(
            self,
            otu_ids: List[str],
            path: Path,
            processes: int
    ) -> Tuple[Path, Dict[str, int]]:
        """
        Generate a FASTA file and Bowtie2 index for all of the isolates of the OTUs specified by ``otu_ids``.

        :param otu_ids: the list of OTU IDs for which to generate and index
        :param path: the path to the reference index directory
        :param processes: how many processes are available for external program calls
        :return: a tuple containing the path to the Bowtie2 index, FASTA files, and a dictionary of the lengths
            of all sequences keyed by their IDS
        """
