"""Fixtures for getting runtime configuration details."""
from virtool_workflow import fixture
from virtool_workflow_runtime.config.configuration import VirtoolConfiguration


@fixture
def temp_path_str(config: VirtoolConfiguration) -> str:
    return config.temp_path


@fixture
def data_path_str(config: VirtoolConfiguration) -> str:
    return config.data_path


@fixture(alt_names=["number_of_processes", "process_limit"])
def proc(config: VirtoolConfiguration) -> int:
    """The number of allowable processes for the currently executed workflow/job."""
    return config.proc


@fixture(alt_names=["memory_limit", "RAM_limit"])
def mem(config: VirtoolConfiguration) -> int:
    return config.mem


@fixture(alt_names=["redis_url"])
def redis_connection_string(config: VirtoolConfiguration) -> str:
    return config.redis_connection_string


@fixture(alt_names=["sentry_enabled", "use_sentry"])
def no_sentry(config: VirtoolConfiguration) -> bool:
    return config.use_sentry


@fixture(alt_names=["DEV", "dev_mode"])
def development_mode(config: VirtoolConfiguration) -> bool:
    return config.development_mode


@fixture(alt_names=["db_name", "mongo_db_name", "database_name"])
def mongo_database_name(config: VirtoolConfiguration) -> str:
    return config.mongo_database_name


@fixture(alt_names=["db_conn_string", "mongo_conn_string",
                    "db_conn_str", "mongo_conn_str",
                    "mongo_connection_string"])
def db_connection_string(config: VirtoolConfiguration) -> str:
    return config.mongo_connection_string




