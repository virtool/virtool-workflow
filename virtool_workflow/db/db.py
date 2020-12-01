"""Central module for database access. """
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow_runtime.config.configuration import db_name, db_connection_string

from typing import Dict, Any, Optional

_db = VirtoolDatabase(db_name(), db_connection_string())


async def fetch_document_by_id(id_: str, collection_name: str) -> Optional[Dict[str, Any]]:
    """Fetch the document with the given ID from a specific Virtool database collection."""
    document = _db[collection_name].find_one(dict(_id=id_))
    if document:
        document["id"] = document["_id"]
    return document

