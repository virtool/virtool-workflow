"""Central module for database access. """
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow_runtime.config.configuration import db_name, db_connection_string

from typing import Dict, Any

_db = VirtoolDatabase(db_name(), db_connection_string())


async def fetch_subtraction_document(id_: str) -> Dict[str, Any]:
    subtraction = await _db["subtractions"].find_one(dict(_id=id_))

    if subtraction:
        subtraction["id"] = subtraction["_id"]
        return subtraction
