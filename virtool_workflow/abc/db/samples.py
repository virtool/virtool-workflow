from abc import ABC, abstractmethod
from typing import Dict, Any, List
from virtool_workflow.uploads.files import DownloadableFileUpload


class AbstractSampleProvider(ABC):

    @abstractmethod
    def recalculate_workflow_tags(self):
        """Recalculate workflow tags for samples associated with the current job."""
        ...

    @abstractmethod
    def set_quality(self, quality: Dict[str, Any]):
        """Store the quality of the current sample and mark it as ready."""

    @abstractmethod
    def delete_sample(self):
        """Delete the sample associated with the current Job."""

    @abstractmethod
    def set_files(self, uploads: List[DownloadableFileUpload]):
        ...

