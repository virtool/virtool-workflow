from virtool_workflow.config.configuration import config_fixture

REDIS_CONNECTION_STRING_ENV = "VT_REDIS_CONNECTION_STRING"
REDIS_JOB_LIST_NAME_ENV = "VT_REDIS_JOB_LIST_NAME"
REDIS_CANCEL_LIST_NAME_ENV = "VT_CANCEL_LIST_NAME"
NO_SENTRY_ENV = "VT_NO_SENTRY"
DOCER_DAEMON_ENV = "VT_DOCKER_DAEMON"


@config_fixture(env=REDIS_CONNECTION_STRING_ENV, default="redis://localhost:6379")
def redis_connection_string(_):
    """A fixture for the redis connection string/url."""
    ...


@config_fixture(REDIS_JOB_LIST_NAME_ENV, default="channel:jobs")
def redis_job_list_name(_):
    """The name of the job list in redis."""
    ...


@config_fixture(REDIS_CANCEL_LIST_NAME_ENV, default="channel:cancel")
def redis_cancel_list_name(_):
    """The name of the redis list where cancellations are pushed."""
    ...


@config_fixture(env=NO_SENTRY_ENV, default=True)
def no_sentry(_):
    """A flag indicating whether or not to run sentry checks."""
    ...


@config_fixture(env=DOCER_DAEMON_ENV, default=None)
def docker_daemon_url(_):
    """The url for the docker daemon. If not set, the docker daemon running on the host will be used."""
    ...


@config_fixture(env="VT_SWARM_MANAGER_NODES", default=None)
def swarm_manager_nodes(addresses):
    if addresses:
        return addresses.split(",")


@config_fixture(env="VT_SWARM_JOIN_TOKEN", default=None)
def swarm_join_token(_):
    ...


@config_fixture(env="VT_SWARM_LISTEN_ADDRESS", default=None)
def swarm_listen_address(_):
    ...


@config_fixture(env="VT_SWARM_ADVERTISE_ADDRESS", default=None)
def swarm_advertise_address(_):
    ...


@config_fixture(env="VT_SWARM_DATA_PATH_ADDRESS", default=None)
def swarm_data_path_address(_):
    ...
