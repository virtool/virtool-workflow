import json
from pathlib import Path

from virtool_workflow.config.fixtures import options

REDIS_CONNECTION_STRING = "VT_REDIS_CONNECTION_STRING"
REDIS_JOB_LIST_NAME = "VT_REDIS_JOB_LIST_NAME"
REDIS_CANCEL_LIST_NAME = "VT_CANCEL_LIST_NAME"
NO_SENTRY = "VT_NO_SENTRY"
DOCER_DAEMON = "VT_DOCKER_DAEMON"


@options.fixture(default="redis://localhost:6379")
def redis_connection_string(_):
    """A fixture for the redis connection string/url."""
    ...


@options.fixture(default="channel:jobs")
def redis_job_list_name(_):
    """The name of the job list in redis."""
    ...


@options.fixture(default="channel:cancel")
def redis_cancel_list_name(_):
    """The name of the redis list where cancellations are pushed."""
    ...


@options.fixture(default=True)
def no_sentry(_):
    """A flag indicating whether or not to run sentry checks."""
    ...


@options.fixture(default=None)
def docker_daemon_url(_):
    """The url for the docker daemon. If not the docker daemon running on the host will be used."""
    ...


@options.fixture(default=None)
def swarm_manager_nodes(addresses):
    """A comma separated list of one or more manager node addresses."""
    if addresses:
        return addresses.split(",")


@options.fixture(default=None)
def swarm_join_token(_):
    """The secret token required to join the docker swarm."""
    ...


@options.fixture(default=None)
def swarm_listen_address(_):
    """The address which this node will listen on for swarm commands."""
    ...


@options.fixture(default=None)
def swarm_advertise_address(_):
    """The public address which will be advertised if this node becomes a manager of the swarm."""
    ...


@options.fixture(default=None)
def swarm_data_path_address(_):
    """The swarm data path address."""
    ...


@options.fixture(default="default_images.json")
def workflow_to_docker_image(filename):
    """
    A JSON file mapping workflow names to docker image names.

    The image names given should be available via `docker pull`or already present locally.
    """
    json_text = Path(filename).read_text()
    return json.loads(json_text)
