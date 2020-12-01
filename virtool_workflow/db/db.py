"""Central module for database access. """
import virtool_core.caches.db
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow_runtime.config.configuration import db_name, db_connection_string

from typing import Dict, Any, Optional

_db = VirtoolDatabase(db_name(), db_connection_string())


async def fetch_document_by_id(id_: str, collection_name: str) -> Optional[Dict[str, Any]]:
    """Fetch the document with the given ID from a specific Virtool database collection."""
    document = await _db[collection_name].find_one(dict(_id=id_))
    if document:
        document["id"] = document["_id"]
    return document


async def find_cache_document(query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find a cache document using the given query."""
    return await _db["caches"].find_one(query)


async def create_cache_document(sample_id: str, trimming_parameters: Dict[str, Any], paired: bool):
    """Create a new cache document."""
    return await virtool_core.caches.db.create(_db, sample_id, trimming_parameters, paired)


async def update_analysis_with_cache_id(analysis_id: str, cache_id: str):
    """Set the `id` field of the analysis document to the cache id."""
    return await _db["analyses"].update_one({"_id": analysis_id}, {
        "$set": {
            "cache": {
                "id": cache_id
            }
        }
    })


