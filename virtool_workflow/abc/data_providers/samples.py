from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

from virtool_workflow.analysis.utils import ReadPaths
from virtool_workflow.data_model import Sample
from virtool_workflow.data_model.files import VirtoolFileFormat


class AbstractSampleProvider(ABC):

    @abstractmethod
    async def get(self) -> Sample:
        """Fetch the sample associated with the current job."""
        ...

    @abstractmethod
    async def finalize(self, quality: Dict[str, Any]):
        """Store the quality of the current sample and mark it as ready."""

    @abstractmethod
    async def delete(self):
        """Delete the sample associated with the current Job."""
        ...

    @abstractmethod
    async def upload(self, path: Path, format: VirtoolFileFormat):
        """Upload a file associated with the current sample."""
        ...

    @abstractmethod
    async def download_reads(self, target_path: Path, paired: bool = None) -> ReadPaths:
        """
        Download reads for the current sample.

        :param target_path: The path where the file(s) will be downloaded.
        :param paired: Indicates that the sample is paired. If not provided then the sample
            will be fetched again via `.get()`.
        """
        ...

    @abstractmethod
    async def download_artifact(self, filename: str, target_path: Path):
        """
        Download an artifact associated with the current sample.

        :param: The file name of the artifact.
        :param: The path where the file should be stored.
        """

    def __await__(self):
        return self.get().__await__()
