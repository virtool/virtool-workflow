"""Functions for accessing the Virtool database"""
from os import getenv
from virtool_core.db.core import DB
from virtool_core.utils import timestamp
from virtool_workflow import Workflow, WorkflowExecutionContext
from motor.motor_asyncio import AsyncIOMotorClient
from .job import Job

DATABASE_CONNECTION_URL_ENV = "DATABASE_CONNECTION_URL"
DATABASE_CONNECTION_URL_DEFAULT = "mongodb://localhost:27017"

def connect_db_for_job(job: Job):
    pass

class RuntimeDatabaseConnection:
    """Send updates to the Virtool jobs database during the lifecycle of a running Workflow."""

    def __init__(
            self,
            workflow: Workflow,
            context: WorkflowExecutionContext,
            job_id: str,
            mongo_connection_string: str = getenv(DATABASE_CONNECTION_URL_ENV,
                                                  default=DATABASE_CONNECTION_URL_DEFAULT)
    ):
        self.job = Job(job_id, workflow, context)

        self.client = AsyncIOMotorClient(mongo_connection_string)
        self.db = DB(self.client, enqueue_change=None)
        self.jobs = self.db.jobs

        self.job.context.on_update(self._send_update)

    async def _send_update(self, context: WorkflowExecutionContext, update: str):
        await self.jobs.update_one({"_id": self.job.id}, {
            "$set": {
                "state": str(self.job.context.state)
            },
            "$push": {
                "status": {
                    "state": str(self.job.context.state),
                    "stage": self.job.workflow.steps[self.job.context.current_step - 1].__name__,
                    "error": self.job.context.error,
                    "progress": self.job.context.progress,
                    "update": update,
                    "timestamp": timestamp(),
                }
            }
        })


