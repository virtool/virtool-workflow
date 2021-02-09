import json
from pathlib import Path

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
    """A comma separated list of one or more manager node addresses."""
    if addresses:
        return addresses.split(",")


@config_fixture(env="VT_SWARM_JOIN_TOKEN", default=None)
def swarm_join_token(_):
    """The secret token required to join the docker swarm."""
    ...


@config_fixture(env="VT_SWARM_LISTEN_ADDRESS", default=None)
def swarm_listen_address(_):
    """The address which this node will listen on for swarm commands."""
    ...


@config_fixture(env="VT_SWARM_ADVERTISE_ADDRESS", default=None)
def swarm_advertise_address(_):
    """The public address which will be advertised if this node becomes a manager of the swarm."""
    ...


@config_fixture(env="VT_SWARM_DATA_PATH_ADDRESS", default=None)
def swarm_data_path_address(_):
    """The swarm data path address."""
    ...


@config_fixture(env="VT_DOCKER_IMAGE_MAP_JSON", default="default_images.json")
def workflow_to_docker_image(filename):
    """
    A JSON file mapping workflow names to docker image names.

    The image names given should be available via `docker pull`, or already present locally.
    """
    json_text = Path(filename).read_text()
    return json.loads(json_text)
