import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

import aiofiles
from pyfixtures import fixture
from virtool_core.models.analysis import Analysis
from virtool_core.models.index import Index
from virtool_core.models.job import Job
from virtool_core.models.reference import ReferenceNested
from virtool_core.utils import decompress_file

from virtool_workflow.api.client import APIClient
from virtool_workflow.data.files import VirtoolFileFormat
from virtool_workflow.errors import MissingJobArgument


@dataclass
class WFIndex:
    """Represents a Virtool reference index for use in analysis workflows."""

    id: str
    """The ID of the index."""

    path: Path
    """The path to the index directory in the workflow's work directory."""

    manifest: dict[str, int | str]
    """The manifest (OTU ID: OTU Version) for the index."""

    reference: ReferenceNested
    """The parent reference."""

    sequence_lengths: dict[str, int]
    """A dictionary of the lengths of all sequences keyed by their IDs."""

    sequence_otu_map: dict[str, str]
    """A dictionary of the OTU IDs for all sequences keyed by their sequence IDs."""

    @property
    def bowtie_path(self) -> Path:
        """
        The path to the Bowtie2 index prefix for the Virtool index.

        """
        return self.path / "reference"

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

    def get_otu_id_by_sequence_id(self, sequence_id: str) -> str:
        """
        Get the ID of the parent OTU for the given ``sequence_id``.

        :param sequence_id: the sequence ID
        :return: the matching OTU ID

        """
        try:
            return self.sequence_otu_map[sequence_id]
        except KeyError:
            raise ValueError("The sequence_id does not exist in the index")

    def get_sequence_length(self, sequence_id: str) -> int:
        """
        Get the sequence length for the given ``sequence_id``.

        :param sequence_id: the sequence ID
        :return: the length of the sequence

        """
        try:
            return self.sequence_lengths[sequence_id]
        except KeyError:
            raise ValueError("The sequence_id does not exist in the index")

    async def write_isolate_fasta(
        self,
        otu_ids: list[str],
        path: Path,
    ) -> dict[str, int]:
        """
        Generate a FASTA file for all the isolates of the OTUs specified by ``otu_ids``.

        :param otu_ids: the list of OTU IDs for which to generate and index
        :param path: the path to the reference index directory
        :return: a dictionary of the lengths of all sequences keyed by their IDS

        """
        unique_otu_ids = set(otu_ids)

        def func():
            with open(self.json_path) as f:
                otus = [otu for otu in json.load(f) if otu["_id"] in unique_otu_ids]

            lengths = {}

            with open(path, "w") as f:
                for otu in otus:
                    for isolate in otu["isolates"]:
                        for sequence in isolate["sequences"]:
                            f.write(f">{sequence['_id']}\n{sequence['sequence']}\n")
                            lengths[sequence["_id"]] = len(sequence["sequence"])

            return lengths

        return await asyncio.to_thread(func)


class WFNewIndex:
    def __init__(
        self, api: APIClient, index_id: str, manifest: dict[str, int | str], path: Path
    ):
        self._api = api

        self.id = index_id
        """The ID of the index."""

        self.manifest = manifest
        """The manifest (OTU ID: OTU Version) for the index."""

        self.path = path
        """The path to the index directory in the workflow's work directory."""

    async def delete(self):
        await self._api.delete(f"/indexes/{self.id}")

    async def finalize(self):
        """Finalize the current index."""
        await self._api.patch_json(f"/indexes/{self.id}", {})

    async def upload(
        self, path: Path, fmt: VirtoolFileFormat = "fasta", name: str | None = None
    ):
        """
        Upload a file to associate with the index being built.

        Allowed file names are:

        - reference.json.gz
        - reference.fa.gz
        - reference.1.bt2
        - reference.2.bt2
        - reference.3.bt2
        - reference.4.bt4
        - reference.rev.1.bt2
        - reference.rev.2.bt2

        :param path: The path to the file.
        :param fmt: The format of the file.
        :param name: An optional name for the file different that its name on disk.
        :return: A :class:`VirtoolFile` object.
        """
        return await self._api.put_file(
            f"/indexes/{self.id}/files/{name or path.name}",
            path,
            fmt,
        )

    @property
    def json_path(self) -> Path:
        """
        The path to the JSON representation of the reference index in the workflow's
        work directory.

        """
        return self.path / "otus.json"


@fixture
async def index(
    _api: APIClient,
    analysis: Analysis,
    proc: int,
    work_path: Path,
) -> WFIndex:
    """The :class:`WFIndex` for the current analysis job."""
    id_ = analysis.index.id

    index_json = await _api.get_json(f"/indexes/{id_}")
    index_ = Index(**index_json)

    index_work_path = work_path / "indexes" / index_.id
    await asyncio.to_thread(index_work_path.mkdir, parents=True, exist_ok=True)

    for name in (
        "otus.json.gz",
        "reference.json.gz",
        "reference.fa.gz",
        "reference.1.bt2",
        "reference.2.bt2",
        "reference.3.bt2",
        "reference.4.bt2",
        "reference.rev.1.bt2",
        "reference.rev.2.bt2",
    ):
        await _api.get_file(f"/indexes/{id_}/files/{name}", index_work_path / name)

    await asyncio.to_thread(
        decompress_file,
        index_work_path / "reference.fa.gz",
        index_work_path / "reference.fa",
        proc,
    )

    json_path = index_work_path / "otus.json"

    await asyncio.to_thread(
        decompress_file,
        index_work_path / "otus.json.gz",
        index_work_path / json_path,
        proc,
    )

    async with aiofiles.open(json_path) as f:
        data = json.loads(await f.read())

    sequence_lengths = {}
    sequence_otu_map = {}

    for otu in data:
        for isolate in otu["isolates"]:
            for sequence in isolate["sequences"]:
                sequence_id = sequence["_id"]

                sequence_otu_map[sequence_id] = otu["_id"]
                sequence_lengths[sequence_id] = len(sequence["sequence"])

    return WFIndex(
        id=id_,
        path=index_work_path,
        manifest=index_.manifest,
        reference=index_.reference,
        sequence_lengths=sequence_lengths,
        sequence_otu_map=sequence_otu_map,
    )


@fixture
async def new_index(_api: APIClient, job: Job, work_path: Path) -> WFNewIndex:
    """
    The :class:`.WFNewIndex` for an index being created by the current job.
    """
    try:
        id_ = job.args["index_id"]
    except KeyError:
        raise MissingJobArgument("Missing jobs args key 'index_id'")

    index_json = await _api.get_json(f"/indexes/{id_}")
    index_ = Index(**index_json)

    index_work_path = work_path / "indexes" / index_.id
    await asyncio.to_thread(index_work_path.mkdir, parents=True, exist_ok=True)

    await _api.get_file(
        f"/indexes/{id_}/files/otus.json.gz", index_work_path / "otus.json.gz"
    )

    return WFNewIndex(
        api=_api,
        index_id=id_,
        manifest=index_.manifest,
        path=index_work_path,
    )
