"""Central module for database access. """
from virtool_core.db.bindings import BINDINGS
import virtool_core.caches.db
import virtool_core.db.core
import virtool_core.samples.db
from pathlib import Path
from typing import Dict, Any, Optional

from virtool_workflow_runtime.config.configuration import db_name, db_connection_string
from virtool_workflow_runtime.db import VirtoolDatabase

_db = VirtoolDatabase(db_name(), db_connection_string())

COLLECTION_NAMES = [binding.collection_name for binding in BINDINGS]


async def fetch_document_by_id(id_: str, collection_name: str) -> Optional[Dict[str, Any]]:
    """Fetch the document with the given ID from a specific Virtool database collection."""
    document = await _db[collection_name].find_one(dict(_id=id_))
    if document:
        document["id"] = document["_id"]
    return document


async def find_document(collection_name: str, *args, **kwargs):
    """Find a document in a database collection based on the given query."""
    return await _db[collection_name].find_one(*args, **kwargs)


async def find_cache_document(query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find a cache document using the given query."""
    return await _db["caches"].find_one(query)


async def create_cache_document(sample_id: str, trimming_parameters: Dict[str, Any],
                                paired: bool, quality: Dict = None):
    """Create a new cache document."""
    document = await virtool_core.caches.db.create(_db, sample_id, trimming_parameters, paired)

    if quality:
        await _db["caches"].update_one(dict(_id=document["id"]), {"$set": {
            "quality": quality
        }})


async def update_analysis_with_cache_id(analysis_id: str, cache_id: str):
    """Set the `id` field of the analysis document to the cache id."""
    return await _db["analyses"].update_one({"_id": analysis_id}, {
        "$set": {
            "cache": {
                "id": cache_id
            }
        }
    })


async def delete_cache(cache_id: str):
    """Delete the cache with the given id."""
    return await _db["caches"].delete_one({"_id": cache_id})


async def delete_analysis(analysis_id: str):
    """Delete the analysis with the given id."""
    return await _db["analyses"].delete_one({"_id": analysis_id})


async def recalculate_workflow_tags_for_sample(sample_id):
    """Recalculate the workflow tags for a sample."""
    return await virtool_core.samples.db.recalculate_workflow_tags(_db, sample_id)


async def store_result(id_: str, result: Dict[str, Any], collection: str, file_results_location: Path):
    """Store the result onto the document specified by `id_` in the collection specified by `collection`."""
    await _db.store_result(id_, _db[collection], result, file_results_location)

