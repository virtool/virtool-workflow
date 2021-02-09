from virtool_workflow.execution.hooks.fixture_hooks import FixtureHook

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

__all__ = [
    "on_start",
    "on_exit",
    "on_redis_connect",
    "on_init",
    "on_load_config",
    "on_job_cancelled",
    "on_docker_connect",
    "on_join_swarm",
]
