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
data_path_str = environment_variable_fixture("data_path_str", DATA_PATH_ENV, default=f"{os.getcwd()}/virtool")

proc = environment_variable_fixture("proc",
                                    PROC_ENV,
                                    alt_names=("number_of_processes", "process_limit"),
                                    default=2)

mem = environment_variable_fixture("mem",
                                   MEM_ENV,
                                   alt_names=("memory_limit", "RAM_limit"),
                                   default=8)

redis_connection_string = environment_variable_fixture(
    "redis_connection_str",
    REDIS_CONNECTION_STRING_ENV,
    alt_names=("redis_url",),
    default="redis://localhost:6379"
)

no_sentry = environment_variable_fixture("no_sentry", NO_SENTRY_ENV, default=True)
dev_mode = environment_variable_fixture("dev_mode", DEVELOPMENT_MODE_ENV, default=False)
db_name = environment_variable_fixture("db_name", MONGO_DATABASE_NAME_ENV, default="virtool")
db_connection_string = environment_variable_fixture(
    "db_connection_string",
    MONGO_DATABASE_CONNECTION_STRING_ENV,
    alt_names=("db_conn_string", "db_conn_url", "db_connection_url"),
    default="mongodb://localhost:27017",
)



