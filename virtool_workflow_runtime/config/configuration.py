from dataclasses import dataclass

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Type, Callable, Union

import virtool_workflow
import virtool_workflow.storage.paths
from virtool_workflow import hooks
from virtool_workflow.fixtures.providers import DictProvider
from virtool_workflow_runtime.config.environment import ENV_VARIABLE_TYPE

DATA_PATH_ENV = "VT_DATA_PATH"
TEMP_PATH_ENV = "VT_TEMP_PATH"
PROC_ENV = "VT_PROC"
MEM_ENV = "VT_MEM"
REDIS_CONNECTION_STRING_ENV = "VT_REDIS_CONNECTION_STRING"
REDIS_JOB_LIST_NAME_ENV = "VT_REDIS_JOB_LIST_NAME"
NO_SENTRY_ENV = "VT_NO_SENTRY"
DEVELOPMENT_MODE_ENV = "VT_DEV"
MONGO_DATABASE_CONNECTION_STRING_ENV = "VT_DB_CONNECTION_STRING"
MONGO_DATABASE_NAME_ENV = "VT_DB_NAME"


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
config_fixtures = DictProvider()


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

        options[name] = ConfigOption(name=name, type=type_, help=help_, fixture=self)

    def __call__(self, *args, **kwargs):
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
        type_: Type[ENV_VARIABLE_TYPE] = str,
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

    return _config_fixture


async def create_config(scope, **kwargs) -> SimpleNamespace:
    """
    Create a namespace containing all config options which have been defined.

    The created namespace will be added to the scope as a fixture.

    :param scope: The WorkflowFixtureScope for the current context.
    :param kwargs: Values for any config options to be used before the fixtures.
    :return SimpleNamespace: A namespace containing any available config options.
    """
    config = SimpleNamespace()
    for name, _, _, _, _, fixture in options:
        if name in kwargs and kwargs[name] is not None:
            setattr(config, name, kwargs[name])
            options[name].fixture.override_value = kwargs[name]
        else:
            value = await scope.instantiate(options[name])
            setattr(config, name, value)

    await hooks.on_load_config.trigger(config)

    return config


@config_fixture(env=TEMP_PATH_ENV, default=f"{os.getcwd()}/temp")
def work_path(value: str) -> Path:
    """The path where temporary data should be stored."""
    with virtool_workflow.storage.paths.context_directory(value) as temp:
        yield temp


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


@config_fixture(env=REDIS_CONNECTION_STRING_ENV, default="redis://localhost:6379")
def redis_connection_string(_):
    """A fixture for the redis connection string/url."""
    ...


@config_fixture(REDIS_JOB_LIST_NAME_ENV, default="job_list")
def redis_job_list_name(_):
    """The name of the job list in redis."""
    ...


@config_fixture(env=NO_SENTRY_ENV, default=True)
def no_sentry(_):
    """A flag indicating whether or not to run sentry checks."""
    ...


@config_fixture(env=DEVELOPMENT_MODE_ENV, default=False)
def dev_mode(_):
    """A flag indicating that development mode is enabled."""
    ...


@config_fixture(env=MONGO_DATABASE_NAME_ENV, default="virtool")
def db_name(_):
    """The MongoDB database name."""
    ...


@config_fixture(env=MONGO_DATABASE_CONNECTION_STRING_ENV, default="mongodb://localhost:27017")
def db_connection_string(_):
    """The MongoDB database connection string/url."""
    ...


