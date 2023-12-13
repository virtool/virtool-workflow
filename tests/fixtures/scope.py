from importlib import import_module
from pathlib import Path

import pytest
from pyfixtures import FixtureScope
from structlog import get_logger

from tests.fixtures.data import Data
from virtool_workflow.api.client import api_client
from virtool_workflow.runtime.config import RunConfig


@pytest.fixture
async def scope(data: Data, jobs_api_connection_string: str, work_path: Path):
    """The same fixture scope that is used when running workflows."""
    import_module("virtool_workflow.data")

    job = data.job

    async with api_client(jobs_api_connection_string, job.id, job.key) as api:
        async with FixtureScope() as scope:
            config = RunConfig(
                dev=False,
                jobs_api_connection_string=jobs_api_connection_string,
                mem=8,
                proc=2,
                work_path=work_path,
            )

            scope["_config"] = config
            scope["_api"] = api
            scope["_error"] = None
            scope["_job"] = job
            scope["_state"] = job.state
            scope["_step"] = job.stage
            scope["_workflow"] = job.workflow

            scope["logger"] = get_logger("workflow")
            scope["mem"] = config.mem
            scope["proc"] = config.proc
            scope["results"] = {}
            scope["work_path"] = work_path

            yield scope
