"""
Fixtures that expose configuration values.

"""
import os
from pathlib import Path

import virtool_workflow
import virtool_workflow.storage.paths
from .group import ConfigFixtureGroup

options = ConfigFixtureGroup()


@options.fixture(default=f"{os.getcwd()}temp")
def work_path(value: str) -> Path:
    """The path where temporary data should be stored."""
    with virtool_workflow.storage.paths.context_directory(value) as temp:
        yield temp


@options.fixture(default=2, type_=int)
def proc(_):
    """The number of processes as an integer."""
    ...


@options.fixture(default=8, type_=int)
def mem(_):
    """The amount of RAM in GB available for use."""
    ...


@options.fixture(default=False)
def dev_mode(_):
    """A flag indicating that development mode is enabled."""
    ...


@options.fixture(default="http://localhost:9950/api")
def jobs_api_url(_):
    """The url for the Virtool Jobs API."""
    ...


@options.fixture(type_=bool, default=True)
def is_analysis_workflow(_):
    """A flag indicating that analysis fixtures should be loaded."""
    ...


@options.fixture(default="workflow.py")
def workflow_file_path(name) -> Path:
    """The python script containing the workflow code."""
    return Path(name)


@options.fixture(default=None)
def job_id(_):
    """The database id of the job document for this workflow run."""
    ...


@options.fixture(default="init.py")
def init_file(name) -> Path:
    """A python script which will be executed before the workflow is loaded."""
    path = Path(name)
    if path.suffix != ".py":
        raise ValueError("init file must be a python file.")
    return path


@options.fixture(default="fixtures.py")
def fixtures_file(name) -> Path:
    """A python script containing fixtures which will be loaded before the workflow is executed."""
    path = Path(name)
    if path.suffix != ".py":
        raise ValueError("init file must be a python file.")
    return path
