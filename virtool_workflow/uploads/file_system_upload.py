import shutil
from pathlib import Path
from typing import List

from virtool_workflow import fixture
from virtool_workflow.abc import AbstractFileUploader
from virtool_workflow.uploads.files import FileUpload
from virtool_workflow.execution.run_in_executor import FunctionExecutor


class DirectoryFileUploader(AbstractFileUploader):
    """Move marked files to a directory."""

    def __init__(self, upload_directory: Path, run_in_executor: FunctionExecutor):
        if not upload_directory.exists():
            raise FileNotFoundError(upload_directory)

        self.upload_directory = upload_directory
        self._marks: List[FileUpload] = []
        self._run_in_executor = run_in_executor

    def mark(self, upload: FileUpload):
        self._marks.append(upload)

    async def upload(self):
        for file_upload in self._marks:
            await self._run_in_executor(
                shutil.move,
                file_upload.path,
                self.upload_directory/file_upload.path.name
            )




