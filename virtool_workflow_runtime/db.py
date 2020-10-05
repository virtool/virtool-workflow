"""Functions for accessing the Virtool database"""
from os import getenv
from virtool_core.db.core import DB
from virtool_core.utils import timestamp
from virtool_workflow import Workflow, WorkflowExecutionContext
from motor.motor_asyncio import AsyncIOMotorClient
from .job import Job

DATABASE_CONNECTION_URL_ENV = "DATABASE_CONNECTION_URL"
DATABASE_CONNECTION_URL_DEFAULT = "mongodb://localhost:27017"
DATABASE_NAME = "virtool"


def set_database_updates(job: Job, database_name=DATABASE_NAME) -> DB:
    client = AsyncIOMotorClient(getenv(DATABASE_CONNECTION_URL_ENV, default=DATABASE_CONNECTION_URL_DEFAULT))
    db = DB(client[database_name], None)

    async def _send_update(_, update: str):
        await db.jobs.update_one({"_id": job.id}, {
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
    return db


