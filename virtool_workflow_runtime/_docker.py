from asyncio import AbstractEventLoop

import asyncio
import concurrent.futures
import docker
import logging
from typing import List

from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow_runtime._threading import run_async_function_in_thread
from virtool_workflow_runtime.hooks import on_load_config, on_docker_connect, on_join_swarm, on_init, on_docker_event

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


async def docker_event_watcher(client: docker.DockerClient,
                               scope: FixtureScope,
                               main_thread_event_loop: AbstractEventLoop):
    """
    Trigger the `on_docker_event` hook for each incoming docker event.

    :func:`DockerClient.events()` returns a generator yielding docker events. This generator
    is blocking so it can't be used with the main asyncio event loop. As such this function is
    intended to be run in a separate thread.

    The `on_docker_event` hook is triggered using :func:`asyncio.run_coroutine_threadsafe` to avoid thread safety
    issues within the `on_docker_event` callback functions. Though a separate thread is monitoring the docker events,
    the hook callbacks are being executed in the main thread and are scheduled by the asyncio event loop.

    :param client: The docker client
    :param scope: The :class:`FixtureScope` which should be used when triggering the `on_docker_event` hook.
    :param main_thread_event_loop: The asyncio event loop.
    """
    logger.debug("Starting docker event watcher.")
    for event in client.events(decode=True):
        if main_thread_event_loop.is_closed():
            return
        future = asyncio.run_coroutine_threadsafe(on_docker_event.trigger(scope, event), main_thread_event_loop)
        concurrent.futures.wait((future,))


@on_docker_connect
async def start_docker_event_watcher(docker, scope):
    """Start a new thread which watches for docker events."""
    run_async_function_in_thread(docker_event_watcher(docker, scope, asyncio.get_running_loop()))
