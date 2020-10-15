"""Functions for accessing the Virtool database"""
import asyncio
from os import getenv
from typing import Optional, Any

from motor.motor_asyncio import AsyncIOMotorClient

from virtool_core.db.core import DB
from virtool_core.utils import timestamp
from virtool_workflow import WorkflowFixture
from .job import Job

DATABASE_CONNECTION_URL_ENV = "DATABASE_CONNECTION_URL"
DATABASE_CONNECTION_URL_DEFAULT = "mongodb://localhost:27017"
DEFAULT_DATABASE_NAME = "virtool"


class VirtoolDatabase(WorkflowFixture, param_names=["database", "db"]):

    def __init__(self, db_name: Optional[str] = None, db_conn_url: Optional[str] = None):
        """
        An interface to the Virtool database

        :param db_name: The name of the MongoDB database
        :param db_conn_url: The MongoDB connection URL
        """
        if not db_conn_url:
            db_conn_url = getenv(DATABASE_CONNECTION_URL_ENV, default=DATABASE_CONNECTION_URL_DEFAULT)
        if not db_name:
            db_name = DEFAULT_DATABASE_NAME

        self._client = AsyncIOMotorClient(db_conn_url, io_loop=asyncio.get_event_loop())[db_name]
        self._db = DB(self._client, None)

    @staticmethod
    def __fixture__() -> Any:
        """Return an instance of :class:`VirtoolDatabase` to be used as a workflow fixture."""
        return VirtoolDatabase()

    def __getitem__(self, item):
        """
        Get a :class:`motor.motor_asyncio.AsyncIOMotorCollection` instance for a
        particular virtool database collection
        """
        return getattr(self._db, item)

    def send_updates_to_database_for_job(self, job: Job):
        async def _send_update(_, update: str):
            await self._db.jobs.update_one({"_id": job.id}, {
                "$set": {
                    "state": str(job.context.state)
                },
                "$push": {
                    "status": {
                        "state": str(job.context.state),
                        "stage": job.workflow.steps[job.context.current_step - 1].__name__,
                        "error": job.context.error,
                        "progress": job.context.progress,
                        "update": update,
                        "timestamp": timestamp(),
                    }
                }
            })

        job.context.on_update(_send_update)




