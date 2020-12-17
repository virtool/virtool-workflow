import os
from types import SimpleNamespace
from typing import Any, Type, List, Tuple, Optional

from virtool_workflow import WorkflowFixtureScope, WorkflowFixture, hooks
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


options: List[Tuple[str, str, Type[ENV_VARIABLE_TYPE], Optional[Any], str, WorkflowFixture]] = []


def config_option(
        name,
        env,
        default: Any = None,
        type_: Type[ENV_VARIABLE_TYPE] = str,
        help_: str = "",
) -> WorkflowFixture:
    """
    Create a configuration option.

    This creates a fixture for the option with the given name and type. The value
    of the fixture is determined by the environment variable `env`. The option will
    also be added to the virtool_workflow CLI.

    :param name: The name to be used for the workflow fixture. The name used for the CLI option
        will be this name with `_` replaced by `-`. For example, the CLI option for the name
        `workflow_config_option` would be `--workflow-config-option`.
    :param env: The name of an environment variable backing this option.
    :param default: The default value for the fixture if the environment variable is not set.
    :param type_: The expected type of the environment variable. Supported types are `str`, `int`, and `bool`.
    :param help_: A string which is used for the `--help` command in the CLI.
    """

    option_name = f"--{name}".replace("_", "-")

    fixture = environment_variable_fixture(name, env, default, type_=type_)

    options.append((name, option_name, type_, default, help_, fixture))

    return fixture


async def create_config(scope: WorkflowFixtureScope, **kwargs) -> SimpleNamespace:
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
            scope.add_instance(kwargs[name], fixture.param_name)
        else:
            setattr(config, name, await scope.instantiate(fixture))

    await hooks.on_load_config.trigger(config)

    scope.add_instance(config, "config")
    return config


temp_path_str = config_option("temp_path_str", TEMP_PATH_ENV, default=f"{os.getcwd()}/temp",
                              help_="The path where temporary data should be stored.")
"""A fixture for the Virtool temp path as a string."""

data_path_str = config_option("data_path_str", DATA_PATH_ENV, default=f"{os.getcwd()}/virtool",
                              help_="The path where persistent data should be stored.")
"""A fixture for the Virtool data path as a string"""

proc = config_option("number_of_processes",
                     PROC_ENV,
                     default=2,
                     type_=int,
                     help_="The number of cores available for a workflow.")
"""A fixture for the number of processes as an integer."""

mem = config_option("memory_usage_limit",
                    MEM_ENV,
                    default=8,
                    type_=int,
                    help_="The amount of RAM in GB available for use in a workflow.")
"""A fixture for the maximum amount of RAM usage allowable in GB."""

redis_connection_string = config_option(
    "redis_connection_string",
    REDIS_CONNECTION_STRING_ENV,
    default="redis://localhost:6379",
    help_="The URL used to connect to redis.",
)
"""A fixture for the redis connection string/url."""

redis_job_list_name = config_option("job_list_name", REDIS_JOB_LIST_NAME_ENV, default="job_list",
                                    help_="The name of the job list in redis.")
"""A fixture for the name of the redis list from which jobs should be taken."""

no_sentry = config_option("no_sentry", NO_SENTRY_ENV, default=True, help_="Disable sentry reporting.")
"""A fixture for a flag indicating whether or not to run sentry checks."""

dev_mode = config_option("dev_mode", DEVELOPMENT_MODE_ENV, default=False,
                         help_="enable development mode for more detailed logging.")
"""A fixture for a flag indicating that development mode is enabled."""

db_name = config_option("db_name", MONGO_DATABASE_NAME_ENV, default="virtool",
                        help_="""The name to use for the MongoDB database.""")
"""A fixture for the MongoDB database name."""

db_connection_string = config_option(
    "db_connection_string",
    MONGO_DATABASE_CONNECTION_STRING_ENV,
    default="mongodb://localhost:27017",
    help_="The URL used to connect to MongoDB.")
"""A fixture for the MongoDB database connection string/url."""


