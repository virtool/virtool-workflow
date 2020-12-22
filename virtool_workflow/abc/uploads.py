from abc import ABC, abstractmethod
from virtool_workflow.uploads.files import FileUpload


class AbstractFileUploader(ABC):

    @abstractmethod
    def mark(self, upload: FileUpload):
        """Mark a file for uploading."""
        ...

    async def upload(self):
        """Upload marked files."""
        ...