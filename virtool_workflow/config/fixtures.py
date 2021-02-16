import os
from pathlib import Path

import virtool_workflow
import virtool_workflow.storage.paths
from virtool_workflow import fixture
from virtool_workflow.config.configuration import config_fixture

DATA_PATH_ENV = "VT_DATA_PATH"
TEMP_PATH_ENV = "VT_TEMP_PATH"
PROC_ENV = "VT_PROC"
MEM_ENV = "VT_MEM"
DEVELOPMENT_MODE_ENV = "VT_DEV"
API_URL_ENV = "VT_API_URL"
IS_ANALYSIS_WORKFLOW = "VT_IS_ANALYSIS_WORKFLOW"
WORKFLOW_FILE_NAME_ENV = "VT_WORKFLOW_FILE_NAME"
JOB_ID_ENV = "VT_JOB_ID"
INIT_FILE_ENV = "VT_WORKFLOW_INIT_FILE"
FIXTURES_FILE_ENV = "VT_WORKFLOW_FIXTURES_FILE"


@fixture
@config_fixture(env=TEMP_PATH_ENV, default=f"{os.getcwd()}/temp")
def work_path(value: str) -> Path:
    """The path where temporary data should be stored."""
    with virtool_workflow.storage.paths.context_directory(value) as temp:
        yield temp


@fixture
@config_fixture(DATA_PATH_ENV, default=f"{os.getcwd()}/virtool")
def data_path(value: str) -> Path:
    """The path where persistent data should be stored."""
    _data_path = Path(value)
    if not _data_path.exists():
        _data_path.mkdir()
    return _data_path


@fixture
@config_fixture(env=PROC_ENV, default=2, type_=int)
def proc(_):
    """The number of processes as an integer."""
    ...


@fixture
@config_fixture(env=MEM_ENV, default=8, type_=int)
def mem(_):
    """The amount of RAM in GB available for use."""
    ...


@config_fixture(env=DEVELOPMENT_MODE_ENV, default=False)
def dev_mode(_):
    """A flag indicating that development mode is enabled."""
    ...


@config_fixture(env=API_URL_ENV, default="mongodb://localhost:27017")
def virtool_api_url(_):
    """The database connection string/url."""
    ...


@config_fixture(env=DB_ACCESS_IN_WORKFLOW_ENV,
                type_=bool,
                default=False)
def direct_db_access_allowed(_):
    """
    A flag indicating that the database should be made available within the
    workflow code.

    If True, the database will be available as a fixture `database`.
    If False, the database will only be available within specific fixtures
    which are part of the framework, such as `reads`.
    """
    ...


@config_fixture(env=IS_ANALYSIS_WORKFLOW,
                type_=bool,
                default=True)
def is_analysis_workflow(_):
    """A flag indicating that analysis fixtures should be loaded."""
    ...


@config_fixture(env=WORKFLOW_FILE_NAME_ENV, default="workflow.py")
def workflow_file_path(name) -> Path:
    """The python script containing the workflow code."""
    return Path(name)


@config_fixture(env=JOB_ID_ENV, default=None)
def job_id(_):
    """The database id of the job document for this workflow run."""
    ...


@config_fixture(env=INIT_FILE_ENV, default="init.py")
def init_file(name) -> Path:
    """A python script which will be executed before the workflow is loaded."""
    path = Path(name)
    if path.suffix != ".py":
        raise ValueError("init file must be a python file.")
    return path


@config_fixture(env=FIXTURES_FILE_ENV, default="fixtures.py")
def fixtures_file(name) -> Path:
    """A python script containing fixtures which will be loaded before the workflow is executed."""
    path = Path(name)
    if path.suffix != ".py":
        raise ValueError("init file must be a python file.")
    return path
