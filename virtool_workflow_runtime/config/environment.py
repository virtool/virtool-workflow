"""Fixtures for getting runtime configuration details."""
import os
from typing import Optional, Iterable, Type, Union
from virtool_workflow import fixture, WorkflowFixture

TEMP_PATH_ENV = "VT_TEMP_PATH"
DATA_PATH_ENV = "VT_DATA_PATH"
PROC_ENV = "VT_PROC"
MEM_ENV = "VT_MEM"
REDIS_CONNECTION_STRING_ENV = "VT_REDIS_CONNECTION_STRING"
NO_SENTRY_ENV = "VT_NO_SENTRY"
DEVELOPMENT_MODE_ENV = "VT_DEV"
MONGO_DATABASE_CONNECTION_STRING_ENV = "VT_DB_CONNECTION_STRING"
MONGO_DATABASE_NAME_ENV = "VT_DB_NAME"


ENV_VARIABLE_TYPE = Union[str, int, bool]


def environment_variable_fixture(
        name: str,
        variable: str,
        default: Optional[ENV_VARIABLE_TYPE] = None,
        alt_names: Iterable[str] = (),
        type_: Type[ENV_VARIABLE_TYPE] = str,
) -> WorkflowFixture:
    """
    Create a fixture exposing the value of an environment variable.

    :param name: The name of the fixture.
    :param variable: The name of the environment variable to be used.
    :param default: The default value to use if the environment variable is not set.
    :param alt_names: Alternate names for the fixture.
    :param type_: The expected type of the environment variable. Supported types are str, int, and bool.
    """

    def _fixture() -> Union[int, str, bool]:
        var = os.getenv(variable, default=default)
        if not var:
            if default is None:
                raise KeyError(f"{variable} is not set.")
            return default

        if type_ == bool:
            if var in ("True", "true", "Yes", "yes"):
                return True
            else:
                return False

        if type_ == int:
            return int(var)

        return var

    _fixture.__name__ = _fixture.__qualname__ = name

    return fixture(_fixture, alt_names=alt_names)


temp_path_str = environment_variable_fixture("temp_path_str", TEMP_PATH_ENV, default=f"{os.getcwd()}/temp")
"""The path where temporary data should be stored."""

data_path_str = environment_variable_fixture("data_path_str", DATA_PATH_ENV, default=f"{os.getcwd()}/virtool")
"""The path where persistent data should be stored."""

proc = environment_variable_fixture("proc",
                                    PROC_ENV,
                                    alt_names=("number_of_processes", "process_limit"),
                                    default=2)
"""The number of cores available for a workflow."""

mem = environment_variable_fixture("mem",
                                   MEM_ENV,
                                   alt_names=("memory_limit", "RAM_limit"),
                                   default=8)
"""The amount of RAM in GB available for use in a workflow."""

redis_connection_string = environment_variable_fixture(
    "redis_connection_str",
    REDIS_CONNECTION_STRING_ENV,
    alt_names=("redis_url", "redis_connection_string"),
    default="redis://localhost:6379"
)
"""The URL used to connect to redis."""

no_sentry = environment_variable_fixture("no_sentry", NO_SENTRY_ENV, default=True)
"""Option to disable sentry."""

dev_mode = environment_variable_fixture("dev_mode", DEVELOPMENT_MODE_ENV, default=False)
"""Option to enable dev mode for more detailed logging."""

db_name = environment_variable_fixture("db_name", MONGO_DATABASE_NAME_ENV, default="virtool")
"""The name to use for the MongoDB database."""

db_connection_string = environment_variable_fixture(
    "db_connection_string",
    MONGO_DATABASE_CONNECTION_STRING_ENV,
    alt_names=("db_conn_string", "db_conn_url", "db_connection_url"),
    default="mongodb://localhost:27017",
)
"""The URL used to connect to MongoDB."""

__all__ = [
    "no_sentry",
    "dev_mode",
    "db_name",
    "db_connection_string",
    "redis_connection_string",
    "mem",
    "proc",
    "environment_variable_fixture",
    "temp_path_str",
    "data_path_str"
]


