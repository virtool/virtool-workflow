from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

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
    async def download(self):
        """Delete files associated with the current sample."""
        ...
