"""Functions for accessing the Virtool database"""
from os import getenv
from virtool_core.db.core import DB
from virtool_core.utils import timestamp
from virtool_workflow import Workflow, WorkflowExecutionContext
from .job import Job
from motor.motor_asyncio import AsyncIOMotorClient


DATABASE_CONNECTION_URL_ENV = "DATABASE_CONNECTION_URL"
DATABASE_CONNECTION_URL_DEFAULT = "mongodb://localhost:27017"


class RuntimeDatabaseConnection:
    """Send updates to the Virtool jobs database during the lifecycle of a running Workflow."""

    def __init__(self, workflow: Workflow, context: WorkflowExecutionContext):
        self.workflow = workflow
        self.context = context

        self.db_connection_url = getenv(DATABASE_CONNECTION_URL_ENV,
                                           default=DATABASE_CONNECTION_URL_DEFAULT)
        self.client = AsyncIOMotorClient(self.db_connection_url)
        self.db = DB(self.client, enqueue_change=self._on_update)
        self.jobs = self.db.jobs

        self._init_job_entry()


    def _init_job_entry(self):
        """Create a new Job document in the Virtool database."""
        pass


    async def _on_update(self, collection, operation, *ids):
        pass


    async def send_update(self, update: str):
        self.jobs.update_one({"_id": self.job.id}, {
                "$set": {
                    "state": str(self.job.context.state)
                },
                "$push": {
                    "status": {
                        "state": str(self.job.context.state),
                        "stage": self.job.workflow.steps[self.job.context.current_step-1].__name__,
                        "error": self.job.context.error,
                        "progress": self.job.progress,
                        "update": update,
                        "timestamp": timestamp(),
                    }
                }
            })