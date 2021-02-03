from pathlib import Path
from typing import List, Dict, Any, Iterable, Tuple

from virtool_workflow.abc.data_providers import AbstractSampleProvider
from virtool_workflow.abc.db import AbstractDatabaseCollection
from virtool_workflow.uploads.files import FileUpload
from virtool_workflow.data_model import Sample
from virtool_workflow.db.utils import convert_file_uploads_to_documents


def calculate_workflow_tags(analyses: Iterable[dict]) -> dict:
    """
    Calculate the workflow tags (eg. "ip", True) that should be applied to a sample document based on a list of its
    associated analyses.

    :param analyses: the analyses to calculate tags for
    :return: workflow tags to apply to the sample document

    """
    pathoscope = False
    nuvs = False

    for analysis in analyses:
        if pathoscope is not True and analysis["workflow"] in PATHOSCOPE_TASK_NAMES:
            pathoscope = analysis["ready"] or "ip" or pathoscope

        if nuvs is not True and analysis["workflow"] == "nuvs":
            nuvs = analysis["ready"] or "ip" or nuvs

        if pathoscope is True and nuvs is True:
            break

    return {
        "pathoscope": pathoscope,
        "nuvs": nuvs
    }


class SampleDataProvider(AbstractSampleProvider):
    def __init__(self, sample_id: str, samples: AbstractDatabaseCollection, analyses: AbstractDatabaseCollection):
        self.sample_id = sample_id
        self.samples = samples
        self.analyses = analyses

    async def fetch_sample(self) -> Sample:
        sample = await self.samples.get(self.sample_id)

        return Sample(
            id=sample["_id"],
            name=sample["name"],
            host=sample["host"],
            isolate=sample["isolate"],
            locale=sample["locale"],
            library_type=sample["library_type"],
            paired=sample["paired"],
            quality=sample["quality"],
            nuvs=sample["nuvs"],
            pathoscope=sample["pathoscope"],
            files=sample["files"],
        )

    async def recalculate_workflow_tags(self):
        analyses = await self.analyses.find(projection=["ready", "workflow"], sample=dict(id=self.sample_id))
        await self.samples.set(self.sample_id, **calculate_workflow_tags(analyses))

    async def set_quality(self, quality: Dict[str, Any]):
        await self.samples.set(self.sample_id, quality=quality, ready=True)

    async def delete_sample(self):
        await self.samples.delete(self.sample_id)

    async def set_files(self, files: List[Tuple[FileUpload, Path]]):
        await self.samples.set(self.sample_id, files=convert_file_uploads_to_documents(files))

    async def set_prune(self, prune: bool):
        await self.samples.set(self.sample_id, prune=True)

    async def delete_files(self):
        await self.samples.set(self.sample_id, files=None)

    async def release_files(self):
        raise NotImplemented()
