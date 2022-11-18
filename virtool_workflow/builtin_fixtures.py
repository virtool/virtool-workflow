from pathlib import Path
from shutil import rmtree

from pyfixtures import fixture

from virtool_workflow.api.client import authenticated_http
from virtool_workflow.api.jobs import acquire_job
from virtool_workflow.api.uploads import input_files, files_list
from virtool_workflow.data_model.jobs import WFJob


@fixture
def results() -> dict:
    return {}


@fixture
def work_path(config: dict) -> Path:
    """A temporary working directory."""
    path = Path(config["work_path"]).absolute()
    rmtree(path, ignore_errors=True)
    path.mkdir(parents=True)
    yield path
    rmtree(path)


@fixture
def proc(config: dict) -> int:
    """The number of processes to use for multiprocess operations."""
    return config["proc"]


@fixture
def mem(config: dict) -> int:
    """The amount of RAM available to be used."""
    return config["mem"]


@fixture
def jobs_api_connection_string(config: dict) -> str:
    """The URL of the jobs API."""
    return config["jobs_api_connection_string"]


@fixture
def job_id(config: dict) -> str:
    """The ID for the current job"""
    return config["job_id"]


@fixture
async def _job(job_id, acquire_job, scope) -> WFJob:
    """The current job."""
    job = await acquire_job(job_id)

    scope["http"] = await authenticated_http(job.id, job.key, scope["http"])

    return job


__all__ = [
    "_job",
    "acquire_job",
    "jobs_api_connection_string",
    "mem",
    "proc",
    "results",
    "work_path",
    "job_id",
    "input_files",
    "files_list",
]
