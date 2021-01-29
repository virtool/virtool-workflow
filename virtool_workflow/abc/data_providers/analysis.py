from abc import ABC, abstractmethod
from typing import Dict, Any

from virtool_workflow.uploads.files import FileUpload


class AbstractAnalysisProvider(ABC):

    @abstractmethod
    async def store_result(self, result: Dict[str, Any]):
        """
        Set the result for the current job and mark it as ready.

        :param result: A dict representing the results of the current workflow.
        """
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

