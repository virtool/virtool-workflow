import asyncio
import concurrent.futures
import docker
import logging
from asyncio.events import AbstractEventLoop

from virtool_workflow import FixtureScope
from virtool_workflow_runtime._threading import run_async_function_in_thread
from virtool_workflow_runtime.hooks import on_docker_event, on_docker_connect, on_docker_container_exit

logger = logging.getLogger(__name__)


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


@on_docker_event
async def _remove_dead_container_and_trigger_on_container_exit_hook(event, containers, scope):
    """Filter through incoming docker events and trigger `on_docker_container_exit` hook."""
    if event["Action"] == "die":
        if event["id"] in containers:
            dead_container = containers[event["id"]]
            logger.info(f"{dead_container} running {dead_container.image} has exited.")
            del containers[event["id"]]
            await on_docker_container_exit.trigger(scope, dead_container)
