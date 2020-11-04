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


def environment_variable_fixture(
        name: str,
        variable: str,
        default: Optional[str] = None,
        alt_names: Iterable[str] = (),
        type: Type[int, str, bool] = str,
) -> WorkflowFixture:

    def _fixture() -> Union[int, str, bool]:
        var = os.getenv(variable, default=default)
        if not var:
            raise KeyError(f"{variable} is not set.")

        if type == bool:
            if var in ("True", "true", "Yes", "yes"):
                return True
            else:
                return False

        if type == int:
            return int(var)

        return var

    return fixture(_fixture, name=name, alt_names=alt_names)


temp_path_str = environment_variable_fixture("temp_path_str", TEMP_PATH_ENV)
data_path_str = environment_variable_fixture("data_path_str", DATA_PATH_ENV)

proc = environment_variable_fixture("proc", PROC_ENV,
                                    alt_names=("number_of_processes", "process_limit"))

mem = environment_variable_fixture("mem", MEM_ENV,
                                   alt_names=("memory_limit", "RAM_limit"))

redis_connection_string = environment_variable_fixture(
    "redis_connection_str",
    REDIS_CONNECTION_STRING_ENV,
    alt_names=("redis_url",)
)

no_sentry = environment_variable_fixture("no_sentry", NO_SENTRY_ENV)
dev_mode = environment_variable_fixture("dev_mode", DEVELOPMENT_MODE_ENV)
db_name = environment_variable_fixture("db_name", MONGO_DATABASE_NAME_ENV)
db_connection_string = environment_variable_fixture(
    "db_connection_string",
    MONGO_DATABASE_CONNECTION_STRING_ENV,
    alt_names=("db_conn_string", "db_conn_url", "db_connection_url")
)



