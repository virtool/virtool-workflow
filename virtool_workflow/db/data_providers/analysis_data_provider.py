from typing import Dict, Any, Iterable, Tuple
from virtool-workflow.uploads.files import FileUpload
from virtool_workflow.abc.data_providers import AbstractAnalysisProvider
from virtool_workflow.db.db import VirtoolDatabase
from virtool_workflow.abc.db import AbstractDatabaseCollection


class AnalysisDataProvider(AbstractAnalysisProvider):

    def __init__(self, db: AbstractDatabaseCollection, analysis_id: str):

        self.db = db
        self.analysis_id = analysis_id

    async def store_result(self, result: Dict[str, Any]):
        """
        Store the result of a workflow in MongoDB.

        :param result: The result dict from the workflow run.
        """
        async with self.db.update(self.analysis_id) as document:
            document.set("result", result)

    async def store_files(self, uploads: Iterable[Tuple[FileUpload, Path]]):
        async with self.db.update(self.analysis_id) as document:
            document.set(
                "files",
                [{
                    "id": destination_path.name,
                    "name": file_upload.path.name,
                    "description": file_upload.description,
                    "format": file_upload.format,
                    "size": destination_path.stat().st_size
                } for file_upload, destination_path in uploads]
            )

    async def delete(self):
        await self.db.delete(self.analysis_id)
