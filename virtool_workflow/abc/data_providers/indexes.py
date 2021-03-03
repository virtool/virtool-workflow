from abc import ABC, abstractmethod
from pathlib import Path

from virtool_workflow.data_model import Index
from virtool_workflow.data_model.files import VirtoolFileFormat


class AbstractIndexProvider(ABC):

    @abstractmethod
    async def get(self) -> Index:
        """Get the current index."""
        ...

    @abstractmethod
    async def upload(self, path: Path, format: VirtoolFileFormat) -> Path:
        """Upload a file associated with the index."""
        ...

    @abstractmethod
    async def download(self, target_path: Path, *names) -> Path:
        """Download files associated with the index."""
        ...

    @abstractmethod
    async def finalize(self):
        """Mark that the index associated with the current job has a json representation of the reference available."""
        ...

    def __await__(self):
        return self.get().__await__()
