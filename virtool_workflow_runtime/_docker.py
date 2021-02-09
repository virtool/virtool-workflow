import asyncio
import docker
import logging
from typing import List

from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow_runtime.hooks import on_load_config, on_docker_connect, on_join_swarm, on_init, on_docker_event, \
    on_exit

logger = logging.getLogger(__name__)


@on_init
def instantiate_job_container_dict(scope):
    scope["containers"] = {}


@on_load_config
async def create_docker_client(docker_daemon_url, scope):
    if not docker_daemon_url:
        scope["docker"] = docker.from_env()
    else:
        scope["docker"] = docker.DockerClient(base_url=docker_daemon_url)

    scope["docker"].ping()

    await on_docker_connect.trigger(scope)


@on_docker_connect
async def join_swarm(docker: docker.DockerClient,
                     swarm_manager_nodes: List[str],
                     swarm_join_token: str,
                     swarm_listen_address: str,
                     swarm_advertise_address: str,
                     swarm_data_path_address: str,
                     scope: FixtureScope):
    if swarm_manager_nodes:
        logger.info("Joining docker swarm.")
        docker.swarm.join(
            remote_addrs=swarm_manager_nodes,
            join_token=swarm_join_token,
            listen_addr=swarm_listen_address,
            advertise_addr=swarm_advertise_address,
            data_path_addr=swarm_data_path_address,
        )

        await on_join_swarm.trigger(scope)

    logger.info("No docker swarm configured, using a single docker engine only.")


async def start_workflow_container(client: docker.DockerClient,
                                   image: str,
                                   *options: str):
    """
    Start a workflow container.

    :param client: The docker client.
    :param image: The name of the container image for the workflow.
    :param options: Any options which should be provided to the workflow container.
    """
    return client.containers.run(image, [*options], detach=True)


async def async_docker_events(client: docker.DockerClient):
    for event in client.events(decode=True):
        yield event


async def docker_event_watcher(client: docker.DockerClient, scope: FixtureScope):
    logger.debug("Starting docker event watcher.")
    async for event in async_docker_events(client):
        await on_docker_event.trigger(scope, event)


@on_docker_connect
async def start_docker_event_watcher(docker, scope, tasks):
    tasks["docker_event_watcher"] = asyncio.create_task(docker_event_watcher(docker, scope))


@on_exit
async def cancel_docker_event_watcher(tasks):
    tasks["docker_event_watcher"].cancel()
    del tasks["docker_event_watcher"]
