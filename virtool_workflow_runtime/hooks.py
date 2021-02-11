from docker.models.containers import Container

from virtool_workflow.data_model import Job
from virtool_workflow.execution.hooks.fixture_hooks import FixtureHook
from virtool_workflow.utils import coerce_to_coroutine_function

on_load_config = FixtureHook("on_load_config", [], None)

on_init = FixtureHook("on_init", [], None)
"""
Triggered before the configuration is loaded by the CLI. 

Intended for initialization tasks that don't depend on any configuration variables.
"""

on_start = FixtureHook("on_start", [], None)
"""Triggered when the runtime starts, after the configuration is loaded."""

on_redis_connect = FixtureHook("on_redis_connect", [], None)
"""
Triggered when a connection to redis is established. 

The :class:`aioredis.Redis` object is available as a fixture `redis`.
"""

on_docker_connect = FixtureHook("on_docker_connect", [], None)
"""
Triggered when a connection to the docker daemon is established.

The :class:`docker.DockerClient` object is available as a fixture `docker`.
"""

on_docker_event = FixtureHook("on_docker_event", [dict], None)
"""
Triggered when there is an event emitted by the docker daemon.
"""

on_docker_container_exit = FixtureHook("on_docker_container_exit", [Container], None)
"""
Triggered when the `die` event is emitted by the docker daemon.

Callbacks to this hook are passed the container that died as their first argument.
"""

on_join_swarm = FixtureHook("on_join_swarm", [], None)
"""
Triggered when the docker engine is connected to an existing docker swarm.
"""

on_exit = FixtureHook("on_exit", [], None)
"""
Triggered before the process exists.

If the process is exiting due to an exception, the `error` fixture will hold the exception. If the process is 
finishing successfully then the `error` fixture will be None.
"""

on_job_cancelled = FixtureHook("on_job_cancelled", [str], None)

on_job_processed = FixtureHook("on_job_processed", [Job], None)
"""Triggered when a job is processed and it's docker container is started."""

on_job_finished = FixtureHook("on_job_finished", [Job], None)
"""Triggered when a job is finished and it's docker container has exited."""


def on_container_exit(target):
    """Respond to a particular docker container exiting."""

    def _on_specific_container_exit(callback):
        @on_docker_container_exit(once=True)
        async def _watch_for_container(container):
            if container == target:
                await coerce_to_coroutine_function(callback)()

    return _on_specific_container_exit


__all__ = [
    "on_container_exit",
    "on_docker_connect",
    "on_docker_container_exit",
    "on_docker_event",
    "on_exit",
    "on_init",
    "on_job_cancelled",
    "on_job_processed",
    "on_job_finished",
    "on_join_swarm",
    "on_load_config",
    "on_redis_connect",
    "on_start",
]
