"""Functions for accessing the Virtool database"""
from os import getenv
from virtool_core.db.core import DB
from virtool_core.utils import timestamp
from motor.motor_asyncio import AsyncIOMotorClient
from .job import Job
from virtool_workflow import WorkflowFixture

DATABASE_CONNECTION_URL_ENV = "DATABASE_CONNECTION_URL"
DATABASE_CONNECTION_URL_DEFAULT = "mongodb://localhost:27017"
DATABASE_NAME = "virtool"


def connect(database_name=DATABASE_NAME):
    client = AsyncIOMotorClient(getenv(DATABASE_CONNECTION_URL_ENV, default=DATABASE_CONNECTION_URL_DEFAULT))
    return DB(client[database_name], None)


class VirtoolDatabase(WorkflowFixture, param_names=["database", "db"]):

    @staticmethod
    def __fixture__() -> DB:
        return VirtoolDatabase()



def set_database_updates(job: Job, database: DB):

    async def _send_update(_, update: str):
        await database.jobs.update_one({"_id": job.id}, {
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


