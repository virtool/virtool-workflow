from typing import Dict, Any, Iterable, Tuple

from virtool_workflow.abc.data_providers import AbstractAnalysisProvider
from virtool_workflow.abc.db import AbstractDatabaseCollection
from virtool_workflow.uploads.files import FileUpload


class AnalysisDataProvider(AbstractAnalysisProvider):

    def __init__(self, db: AbstractDatabaseCollection, analysis_id: str):

        self.db = db
        self.analysis_id = analysis_id

    async def store_result(self, result: Dict[str, Any]):
        """
        Store the result of a workflow in MongoDB.

        :param result: The result dict from the workflow run.
        """
        await self.db.set(self.analysis_id, result=result)

    async def store_files(self, uploads: Iterable[Tuple[FileUpload, Path]]):
        await self.db.set(
            self.analysis_id,
            files=[{
                "id": destination_path.name,
                "name": file_upload.path.name,
                "description": file_upload.description,
                "format": file_upload.format,
                "size": destination_path.stat().st_size
            } for file_upload, destination_path in uploads]
        )

    async def delete(self):
        await self.db.delete(self.analysis_id)
