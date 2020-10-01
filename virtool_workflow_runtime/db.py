"""Functions for accessing the Virtool database"""
from os import getenv
from virtool_core.db.core import DB
from virtool_core.utils import timestamp
from .job import Job


DATABASE_CONNECTION_URL_ENV = "DATABASE_CONNECTION_URL"
DATABASE_CONNECTION_URL_DEFAULT = "mongodb://localhost:27017"


async def _connect(mongo_url: str) -> DB :
    """Connect to the virtool database"""
    # TODO:
    pass

db_connection_url = os.getenv(DATABASE_CONNECTION_URL_ENV, default=DATABASE_CONNECTION_URL_DEFAULT)
_db = connect(db_connection_url)

async def send_update(job: Job, update: str):
    _db.jobs.update_one({"_id": job.id}, {
            "$set": {
                "state": str(job.context.state)
            },
            "$push": {
                "status": {
                    "state": str(job.context.state),
                    "stage": job.workflow.steps[job.context.current_step-1].__name__,
                    "error": job.error,
                    "progress": job.progress,
                    "update": update
                    "timestamp": timestamp()
                }
            }
        })