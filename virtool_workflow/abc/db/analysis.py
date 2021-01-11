from abc import ABC, abstractmethod
from typing import Dict, Any
from virtool_workflow.uploads.files import FileUpload
from virtool_workflow.abc.db.cache import CacheEntry


class AbstractAnalysisProvider(ABC):

    @abstractmethod
    async def store_result(self, result: Dict[str, Any]):
        """
        Set the result for the current job.

        :param result: A dict representing the results of the current workflow.
        """
        ...

    @abstractmethod
    async def set_ready(self, ready=True):
        """Mark the analysis as "ready", indicating that it's result is ready to be displayed."""
        ...

    @abstractmethod
    async def register_file_upload(self, upload: FileUpload):
        """
        Register that a file is available under the `data_path`.

        :param upload: A FileUpload object representing the file.
        """
        ...

    @abstractmethod
    async def delete(self):
        """Delete the analysis for the current job."""
        ...

    @abstractmethod
    async def add_cache(self, cache_entry: CacheEntry):
        """Add a cache entry to the analysis, to be used if the current analysis job is restarted."""
        ...
