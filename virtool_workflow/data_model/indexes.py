import asyncio
import gzip
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Callable

import aiofiles
from virtool_core.models.index import Index
from virtool_core.utils import decompress_file, compress_file

from virtool_workflow.runtime.run_subprocess import RunSubprocess


async def not_implemented(*_):
    raise NotImplementedError()


class WFIndex:
    """
    Represents a Virtool reference index.

    Use cases:


    1. Access index data when creating an analysis workflow.

       Downloads and provides access to the index JSON, Bowtie2, and FASTA at:
           - :attr:`.bowtie_path`

       Allows lookup of key index values using
           - :meth:`.get_otu_id_by_sequence_id`
           - :meth:`.get_sequence_length`

    """

    def __init__(
        self,
        index: Index,
        path: Path,
        finalize: Callable,
        upload: Callable,
        run_subprocess: RunSubprocess,
    ):
        self.index = index
        self.path = path
        self.finalize = finalize
        self.upload = upload
        self._run_subprocess = run_subprocess

        self.id = index.id
        self.manifest = index.manifest
        self.reference = index.reference

        self._sequence_lengths: Dict[str, int] = {}
        self._sequence_otu_map: Dict[str, str] = {}

    @property
    def bowtie_path(self) -> Path:
        """
        The path to the Bowtie2 index prefix for the Virtool index.

        """
        return self.path / "reference"

    @property
    def compressed_json_path(self) -> Path:
        """
        The path to the gzip-compressed JSON representation of the reference index in
        the workflow's work directory.

        """
        return self.path / "otus.json.gz"

    @property
    def fasta_path(self) -> Path:
        """
        The path to the complete FASTA file for the reference index in the workflow's
        work directory.

        """
        return self.path / "ref.fa"

    @property
    def json_path(self) -> Path:
        """
        The path to the JSON representation of the reference index in the workflow's
        work directory.

        """
        return self.path / "otus.json"

    async def decompress_json(self):
        """
        Decompress the gzipped JSON file stored in the reference index directory.

        This data will be used to generate isolate indexes if required. Populates the
        ``sequence_otu_map`` attribute.

        """
        if self.json_path.is_file():
            raise FileExistsError("Index JSON file has already been decompressed")

        try:
            await asyncio.to_thread(
                decompress_file, self.compressed_json_path, self.json_path
            )
        except gzip.BadGzipFile:
            await asyncio.to_thread(
                shutil.copyfile, self.compressed_json_path, self.json_path
            )

        async with aiofiles.open(self.json_path) as f:
            data = json.loads(await f.read())

        sequence_lengths = {}
        sequence_otu_map = {}

        for otu in data:
            for isolate in otu["isolates"]:
                for sequence in isolate["sequences"]:
                    sequence_id = sequence["_id"]

                    sequence_otu_map[sequence_id] = otu["_id"]
                    sequence_lengths[sequence_id] = len(sequence["sequence"])

        self._sequence_lengths = sequence_lengths
        self._sequence_otu_map = sequence_otu_map

    def get_otu_id_by_sequence_id(self, sequence_id: str) -> str:
        """
        Return the OTU ID associated with the given ``sequence_id``.

        :param sequence_id: the sequence ID
        :return: the matching OTU ID

        """
        try:
            return self._sequence_otu_map[sequence_id]
        except KeyError:
            raise ValueError("The sequence_id does not exist in the index")

    def get_sequence_length(self, sequence_id: str) -> int:
        """
        Get the sequence length for the given ``sequence_id``.

        :param sequence_id: the sequence ID
        :return: the length of the sequence

        """
        try:
            return self._sequence_lengths[sequence_id]
        except KeyError:
            raise ValueError("The sequence_id does not exist in the index")

    async def write_isolate_fasta(
        self,
        otu_ids: List[str],
        path: Path,
        proc: int = 1,
    ) -> Dict[str, int]:
        """
        Generate a FASTA file for all of the isolates of the OTUs specified by
        ``otu_ids``.

        :param otu_ids: the list of OTU IDs for which to generate and index
        :param path: the path to the reference index directory
        :param proc: the number of processes available
        :return: a dictionary of the lengths of all sequences keyed by their IDS

        """
        unique_otu_ids = set(otu_ids)

        async with aiofiles.open(self.json_path) as f:
            data = json.loads(await f.read())

        otus = [otu for otu in data if otu["_id"] in unique_otu_ids]

        lengths = {}

        async with aiofiles.open(path, "w") as f:
            for otu in otus:
                for isolate in otu["isolates"]:
                    for sequence in isolate["sequences"]:
                        await f.write(f">{sequence['_id']}\n{sequence['sequence']}\n")
                        lengths[sequence["_id"]] = len(sequence["sequence"])

        await asyncio.to_thread(compress_file, path, path.with_suffix(".fa.gz"), proc)

        return lengths

    async def build_isolate_index(
        self, otu_ids: List[str], path: Path, processes: int
    ) -> Tuple[Path, Dict[str, int]]:
        """
        Generate a FASTA file and Bowtie2 index for all the isolates of the OTUs
        specified by ``otu_ids``.

        :param otu_ids: the list of OTU IDs for which to generate and index
        :param path: the path to the reference index directory
        :param processes: how many processes are available for external program calls
        :return: a tuple containing the path to the Bowtie2 index, FASTA files, and a
        dictionary of the lengths of all sequences keyed by their IDS

        """
        fasta_path = Path(f"{path}.fa")

        lengths = await self.write_isolate_fasta(otu_ids, fasta_path, processes)

        command = [
            "bowtie2-build",
            "--threads",
            str(processes),
            str(fasta_path),
            str(path),
        ]

        await self._run_subprocess(command)

        return fasta_path, lengths
