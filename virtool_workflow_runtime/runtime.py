"""Main entrypoint(s) to the Virtool Workflow Runtime."""
from concurrent import futures

import aioredis
import asyncio
import logging
from typing import Dict, Any

from virtool_workflow import hooks
from virtool_workflow.analysis.runtime import AnalysisWorkflowRuntime
from virtool_workflow.data_model import Job, Status
from virtool_workflow.execution.workflow_executor import WorkflowError
from virtool_workflow.workflow import Workflow
from virtool_workflow_runtime.config.configuration import db_connection_string, db_name
from virtool_workflow_runtime.config.configuration import redis_connection_string, redis_job_list_name
from virtool_workflow_runtime.fixture_loading import InitializedWorkflowFixtureScope
from ._redis import monitor_cancel, redis_list, connect
from .db import VirtoolDatabase


@hooks.on_load_config
def set_log_level_to_debug(config):
    if config.dev_mode:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


runtime_scope = InitializedWorkflowFixtureScope([
    "virtool_workflow_runtime.config.configuration",
    "virtool_workflow.execution.run_in_executor",
    "virtool_workflow.execution.run_subprocess",
    "virtool_workflow.storage.paths",
    "virtool_workflow.analysis.fixtures"
])


class DirectDatabaseAccessRuntime(AnalysisWorkflowRuntime):
    """Runtime implementation that uses the database directly."""

    def __init__(self,
                 database: VirtoolDatabase,
                 job: Job):
        self.db = database
        super(AnalysisWorkflowRuntime, self).__init__(job)

    @staticmethod
    async def create(job_id: str, db_name: str, db_connection_string: str):
        db = VirtoolDatabase(db_name, db_connection_string)
        job_document = await db["jobs"].find_one(dict(_id=job_id))

        statuses = [
            Status(status["error"], status["progress"], status["stage"], status["state"], status["timestamp"])
            for status in job_document["status"]
        ] if "status" in job_document else []

        print(job_document)

        job = Job(
            job_document["_id"],
            args=job_document["args"],
            mem=job_document["mem"],
            proc=job_document["proc"],
            task=job_document["task"],
            status=statuses,
        )

        return DirectDatabaseAccessRuntime(db, job)
