from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Tuple, Iterable

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
    async def store_files(self, uploads: Iterable[Tuple[FileUpload, Path]]):
        """
        Register that a file is available under the `data_path`.

        :param uploads: An Iterable of :class:`FileUpload` and destination path tuples.
        """
        ...

    @abstractmethod
    async def delete(self):
        """Delete the analysis for the current job."""
        ...
