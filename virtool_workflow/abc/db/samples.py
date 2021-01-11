from abc import ABC, abstractmethod
from typing import Dict, Any, List
from virtool_workflow.uploads.files import DownloadableFileUpload


class AbstractSampleProvider(ABC):

    @abstractmethod
    async def recalculate_workflow_tags(self):
        """Recalculate workflow tags for samples associated with the current job."""
        ...

    @abstractmethod
    async def set_quality(self, quality: Dict[str, Any]):
        """Store the quality of the current sample and mark it as ready."""

    @abstractmethod
    async def delete_sample(self):
        """Delete the sample associated with the current Job."""

    @abstractmethod
    async def set_files(self, uploads: List[DownloadableFileUpload]):
        ...

    @abstractmethod
    async def delete_files(self):
        """Delete files associated with the current sample."""

    @abstractmethod
    async def release_files(self):
        """Mark each file associated with the current sample as unreserved."""

