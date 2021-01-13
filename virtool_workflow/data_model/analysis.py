from dataclasses import dataclass
from abc import ABC, abstractmethod
from virtool_workflow.uploads.files import FileUpload
from typing import Optional


@dataclass(frozen=True)
class Analysis(ABC):
    _id: str
    cache: dict
    index: dict
    reference: dict
    sample: dict
    subtraction: dict
    read_count: Optional[int] = None
    subtracted_count: Optional[int] = None

    @abstractmethod
    async def upload_file(self, file_upload: FileUpload):
        """Mark a file to be uploaded at the end of a workflow run."""
        ...
