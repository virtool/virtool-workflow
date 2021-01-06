"""Central module for database access. """
from virtool_core.db.bindings import BINDINGS
import virtool_core.utils
import virtool_core.caches.db
import virtool_core.db.core
import virtool_core.samples.db
import virtool_workflow.abc
from pathlib import Path
from typing import Dict, Any, Optional, Iterable, Tuple

from virtool_workflow_runtime.config.configuration import db_name, db_connection_string
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow import WorkflowFixture
from virtool_workflow.uploads.files import FileUpload

COLLECTION_NAMES = [binding.collection_name for binding in BINDINGS]


class DirectAccessDatabase(virtool_workflow.abc.AbstractDatabase):

    def __init__(self, db_name: str, db_connection_string: str):
        self.db = VirtoolDatabase(db_name, db_connection_string)

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

    async def set_files_on_analysis(self, files: Iterable[Tuple[FileUpload, Path]], analysis_id: str):
        await self.db["analyses"].update_one(dict(_id=analysis_id), {
            "$set": {
                "files": [{
                    "name": file_upload.name,
                    "description": file_upload.description,
                    "format": file_upload.format,
                    "size": destination_path.stat().st_size
                } for file_upload, destination_path in files]
            }
        })

