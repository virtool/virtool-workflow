import os
from typing import Any, Iterable, Type
from types import SimpleNamespace

from virtool_workflow import WorkflowFixtureScope, fixture
from virtool_workflow_runtime.config.environment import environment_variable_fixture, ENV_VARIABLE_TYPE

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


options = []


def config_option(
        name,
        env,
        default: Any = None,
        type_: Type[ENV_VARIABLE_TYPE] = str,
        alt_names: Iterable[str] = (),
        help_: str = "",
):
    option_name = f"--{name}".replace("_", "-")

    fixture = environment_variable_fixture(name, env, default, alt_names=alt_names, type_=type_)

    options.append((name, option_name, type_, default, help_, fixture))

    return fixture


async def create_config(scope: WorkflowFixtureScope, **kwargs):
    config = SimpleNamespace()
    for name, _, _, _, _, fixture in options:
        if name in kwargs and kwargs[name] is not None:
            setattr(config, name, kwargs[name])
            scope.add_instance(kwargs[name], *fixture.param_names)
        else:
            setattr(config, name, await scope.instantiate(fixture))

    scope.add_instance(config, "config", "configuration")
    return config


temp_path_str = config_option("temp_path_str", TEMP_PATH_ENV, default=f"{os.getcwd()}/temp",
                              help_="The path where temporary data should be stored.")

data_path_str = config_option("data_path_str", DATA_PATH_ENV, default=f"{os.getcwd()}/virtool",
                              help_="The path where persistent data should be stored.")

proc = config_option("proc",
                     PROC_ENV,
                     alt_names=("number_of_processes", "process_limit"),
                     default=2,
                     help_="The number of cores available for a workflow.")

mem = config_option("mem",
                    MEM_ENV,
                    alt_names=("memory_limit", "RAM_limit"),
                    default=8,
                    help_="The amount of RAM in GB available for use in a workflow.")

redis_connection_string = config_option(
    "redis_connection_str",
    REDIS_CONNECTION_STRING_ENV,
    alt_names=("redis_url", "redis_connection_string"),
    default="redis://localhost:6379",
    help_="The URL used to connect to redis.",
)

redis_job_list_name = config_option("job_list_name", REDIS_JOB_LIST_NAME_ENV, default="job_list",
                                    help_="The name of the job list in redis.")

no_sentry = config_option("no_sentry", NO_SENTRY_ENV, default=True, help_="Disable sentry reporting.")

dev_mode = config_option("dev_mode", DEVELOPMENT_MODE_ENV, default=False,
                         help_="enable development mode for more detailed logging.")

db_name = config_option("db_name", MONGO_DATABASE_NAME_ENV, default="virtool",
                        help_="""The name to use for the MongoDB database.""")

db_connection_string = config_option(
    "db_connection_string",
    MONGO_DATABASE_CONNECTION_STRING_ENV,
    alt_names=("db_conn_string", "db_conn_url", "db_connection_url"),
    default="mongodb://localhost:27017",
    help_="The URL used to connect to MongoDB.")


