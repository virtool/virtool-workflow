"""Functions for accessing the Virtool database."""
import asyncio
import json
from typing import Optional, Any, Dict
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DocumentTooLarge

from virtool_core.db.bindings import BINDINGS
from virtool_core.db.core import DB, Collection
from virtool_core.utils import timestamp
from virtool_workflow import WorkflowFixture
from virtool_workflow.execution.workflow_executor import WorkflowExecution


class VirtoolDatabase(WorkflowFixture, param_name="database"):
    """
    An interface to the Virtool database.

    Individual database Collections can be accessed as attributes or as items.

    .. code-block::
        database = VirtoolDatabase()
        caches = database.caches
        # or
        caches = database["caches"]
    """

    def __init__(self,
                 db_name: Optional[str],
                 db_conn_url: Optional[str]):
        """
        :param db_name: The name of the MongoDB database. 'virtool' will
            be used if None is provided.
        :param db_conn_url: The MongoDB connection URL. If None is provided
            the value of the 'DATABASE_CONNECTION_URL` environment variable
            is used. If the variable is not set then 'mongodb://localhost:27017' is used.
        """
        self._client = AsyncIOMotorClient(db_conn_url, io_loop=asyncio.get_event_loop())[db_name]
        self._db = DB(self._client, None)

        for binding in BINDINGS:
            setattr(self, binding.collection_name, getattr(self._db, binding.collection_name))

    @staticmethod
    def __fixture__(db_name: str, db_connection_string: str) -> Any:
        """Return an instance of :class:`VirtoolDatabase` to be used as a workflow fixture."""
        return VirtoolDatabase(db_name, db_connection_string)

    def __getitem__(self, item) -> Collection:
        """Get a particular database collection."""
        return getattr(self._db, item)

    async def send_update(self, job_id: str, context: WorkflowExecution, update: str):
        """
        Send an update to the jobs database.

        :param job_id: Id of the job in the Virtool database
        :param context: The :class:`WorkflowExecutor` instance
        """
        await self["jobs"].update_one({"_id": job_id}, {
            "$set": {
                "state": str(context.state)
            },
            "$push": {
                "status": {
                    "state": str(context.state),
                    "stage": context.workflow.steps[context.current_step - 1].__name__,
                    "error": context.error,
                    "progress": context.progress,
                    "update": update,
                    "timestamp": timestamp(),
                }
            }
        })

    @staticmethod
    async def store_result(id_: str,
                           collection: Collection,
                           results: Dict[str, Any],
                           file_results_location: Path):
        """
        Store a result in the Virtool database and mark the document as ready.

        :param id_: The ID of the document to add results to.
        :param collection: The collection in which to store the results.
        :param results: The results dict to store.
        :param file_results_location: A path to a directory in which the results
            should be stored in the case that they are too large to be stored in
            the database.
        """
        try:
            await collection.update_one({"_id": id_}, {
                "$set": {
                    "results": results,
                    "ready": True
                }
            })
        except DocumentTooLarge:
            (file_results_location/"results.json").write_text(json.dumps(results))

            await collection.update_one({"_id": id_}, {
                "$set": {
                    "results": "file",
                    "ready": True
                }
            })

    @staticmethod
    def store_result_callback(id_: str, collection: Collection, file_results_location: Path):
        async def _store_results(results):
            return await VirtoolDatabase.store_result(id_, collection, results, file_results_location)

        return _store_results
