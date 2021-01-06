"""Central module for database access. """
from virtool_core.db.bindings import BINDINGS
import arrow
import virtool_core.utils
import virtool_core.caches.db
import virtool_core.db.core
import virtool_core.samples.db
from pathlib import Path
from typing import Dict, Any, Optional

from virtool_workflow_runtime.config.configuration import db_name, db_connection_string
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow import WorkflowFixture
from virtool_workflow.uploads.files import FileUpload

COLLECTION_NAMES = [binding.collection_name for binding in BINDINGS]


class DirectAccessDatabase(WorkflowFixture, param_name="database"):

    def __init__(self, db_name: str, db_connection_string: str):
        self.db = VirtoolDatabase(db_name, db_connection_string)

    @staticmethod
    def __fixture__() -> WorkflowFixture:
        return DirectAccessDatabase(db_name(), db_connection_string())

    async def fetch_document_by_id(self, id_: str, collection_name: str) -> Optional[Dict[str, Any]]:
        """Fetch the document with the given ID from a specific Virtool database collection."""
        document = await self.db[collection_name].find_one(dict(_id=id_))
        if document:
            document["id"] = document["_id"]
        return document

    async def find_document(self, collection_name: str, *args, **kwargs):
        """Find a document in a database collection based on the given query."""
        return await self.db[collection_name].find_one(*args, **kwargs)

    async def find_cache_document(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a cache document using the given query."""
        return await self.db["caches"].find_one(query)

    @staticmethod
    async def create_cache_document(self, sample_id: str, trimming_parameters: Dict[str, Any],
                                    paired: bool, quality: Dict = None):
        """Create a new cache document."""
        document = await virtool_core.caches.db.create(self.db, sample_id, trimming_parameters, paired)

        if quality:
            await self.db["caches"].update_one(dict(_id=document["id"]), {"$set": {
                "quality": quality
            }})

    @staticmethod
    async def update_analysis_with_cache_id(self, analysis_id: str, cache_id: str):
        """Set the `id` field of the analysis document to the cache id."""
        return await self.db["analyses"].update_one({"_id": analysis_id}, {
            "$set": {
                "cache": {
                    "id": cache_id
                }
            }
        })

    async def delete_cache(self, cache_id: str):
        """Delete the cache with the given id."""
        return await self.db["caches"].delete_one({"_id": cache_id})

    async def delete_analysis(self, analysis_id: str):
        """Delete the analysis with the given id."""
        return await self.db["analyses"].delete_one({"_id": analysis_id})

    async def recalculate_workflow_tags_for_sample(self, sample_id):
        """Recalculate the workflow tags for a sample."""
        return await virtool_core.samples.db.recalculate_workflow_tags(self.db, sample_id)

    async def store_result(self, id_: str, result: Dict[str, Any], collection: str, file_results_location: Path):
        """Store the result onto the document specified by `id_` in the collection specified by `collection`."""
        await self.db.store_result(id_, self.db[collection], result, file_results_location)

    async def _generate_file_id(self, filename: str) -> str:
        """
        Generate a unique id for a new file. File ids comprise a unique prefix joined to the filename by a dash
        (eg. abc123-reads.fq.gz).

        :param filename: the filename to generate an id with
        :return: the file id

        """
        files = self.db["files"]

        excluded = await files.distinct("_id")
        prefix = virtool_core.utils.random_alphanumeric(length=8, excluded=excluded)

        file_id = f"{prefix}-{filename}"

        if await files.count_documents({"_id": file_id}):
            return await self._generate_file_id(filename)

        return file_id

    async def add_upload_on_analysis_document(self, file_upload: FileUpload, reserved: bool = False):
        file_id = await self._generate_file_id(file_upload.path.name)

        uploaded_at = virtool_core.utils.timestamp()

        document = {
            "_id": file_id,
            "name": file_upload.name,
            "type": file_upload.format,
            "user": None,
            "uploaded_at": uploaded_at,
            "created": False,
            "reserved": reserved,
            "ready": False
        }

        await self.db["analysis"].update_one(document)

        return document

