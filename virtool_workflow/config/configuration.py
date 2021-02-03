from dataclasses import dataclass

import os
from pathlib import Path
from typing import Any, Type, Callable, Union, Literal

import virtool_workflow
import virtool_workflow.storage.paths
from virtool_workflow import hooks, fixture
from virtool_workflow.fixtures.providers import FixtureGroup
from virtool_workflow.fixtures.scope import FixtureScope

DATA_PATH_ENV = "VT_DATA_PATH"
TEMP_PATH_ENV = "VT_TEMP_PATH"
PROC_ENV = "VT_PROC"
MEM_ENV = "VT_MEM"
DEVELOPMENT_MODE_ENV = "VT_DEV"
MONGO_DATABASE_CONNECTION_STRING_ENV = "VT_DB_CONNECTION_STRING"
MONGO_DATABASE_NAME_ENV = "VT_DB_NAME"
USE_IN_MEMORY_DATABASE_ENV = "VT_USE_IN_MEMORY_DATABASE"
DB_ACCESS_IN_WORKFLOW_ENV = "VT_ALLOW_DIRECT_DB_ACCESS"
IS_ANALYSIS_WORKFLOW = "VT_IS_ANALYSIS_WORKFLOW"
WORKFLOW_FILE_NAME_ENV = "VT_WORKFLOW_FILE_NAME"
JOB_ID_ENV = "VT_JOB_ID"
INIT_FILE_ENV = "VT_WORKFLOW_INIT_FILE"
FIXTURES_FILE_ENV = "VT_WORKFLOW_FIXTURES_FILE"


@dataclass(frozen=True)
class ConfigOption:
    name: str
    type: Type[Union[str, int, bool]]
    help: str
    fixture: "ConfigFixture"

    @property
    def option_name(self):
        return f"--{self.name}".replace("_", "-")


options = {}
config_fixtures = FixtureGroup()


class ConfigFixture(Callable):
    def __init__(self, name: str, env: str,
                 type_: Type[Union[str, int, bool]],
                 default: Any, help_: str, transform: Callable = None):
        self.name = name
        self.env = env
        self.type = type_
        self.default = default
        self.help = help_
        self.override_value = None
        self.transform = transform if transform else lambda x: x

        self.__name__ = self.name

        options[name] = ConfigOption(name=name, type=type_, help=help_, fixture=self)

    def __call__(self):
        if self.override_value:
            return self.override_value

        value = os.getenv(self.env, default=self.default)

        if self.type == bool:
            if value in ("True", "true", "Yes", "yes", "y", "Y"):
                return True
            else:
                return False

        if self.type == int:
            return int(value)

        transformed = self.transform(value)

        return transformed if transformed else value


def config_fixture(
        env: str,
        type_: Type[Union[str, int, bool]] = str,
        default: Any = None,
        help_: str = "",
) -> Callable:
    def _config_fixture(transform: Callable[[Union[str, int, bool]], Any]):
        fixture = ConfigFixture(
            name=transform.__name__,
            env=env,
            type_=type_,
            default=default,
            help_=help_ if help_ else transform.__doc__,
            transform=transform
        )

        config_fixtures[fixture.name] = fixture

        return fixture

    return _config_fixture


async def load_config(**kwargs):
    """
    Override config fixture values with those from :obj:`kwargs`.

    Triggers `on_load_config` hook.

    :param kwargs: Values for any config options to be used before the fixtures.
    """
    for option in options.values():
        if option.name in kwargs and kwargs[option.name] is not None:
            option.fixture.override_value = option.fixture.transform(kwargs[option.name]) or kwargs[option.name]

    with FixtureScope(config_fixtures) as config_scope:
        await hooks.on_load_config.trigger(config_scope)


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


@config_fixture(env=PROC_ENV, default=2, type_=int)
def proc(_):
    """The number of processes as an integer."""
    ...


@config_fixture(env=MEM_ENV, default=8, type_=int)
def mem(_):
    """The amount of RAM in GB available for use."""
    ...


@config_fixture(env=DEVELOPMENT_MODE_ENV, default=False)
def dev_mode(_):
    """A flag indicating that development mode is enabled."""
    ...


@config_fixture(env=MONGO_DATABASE_NAME_ENV, default="virtool")
def db_name(_):
    """The database name."""
    ...


@config_fixture(env=MONGO_DATABASE_CONNECTION_STRING_ENV, default="mongodb://localhost:27017")
def db_connection_string(_):
    """The database connection string/url."""
    ...


DBType = Literal["in-memory", "mongo", "proxy"]


@config_fixture(env=USE_IN_MEMORY_DATABASE_ENV,
                default="in-memory")
def db_type(_):
    """
    The type of database to be used for the workflow run.

    Options are:
        - in-memory
        - mongo
        - proxy

    A in-memory database is used by default.

    If `mongo` or `proxy` is selected, then the `db_connection_string`
    fixture will be used to connect to the database.
    """
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
