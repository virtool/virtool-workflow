from virtool_workflow.execution.hooks import on_load_config
from virtool_workflow.execution.hooks.fixture_hooks import FixtureHook

on_init = FixtureHook("on_init", [], None)

on_start = FixtureHook("on_start", [], None)

on_redis_connect = FixtureHook("on_redis_connect", [], None)

on_exit = FixtureHook("on_exit", [], None)

on_job_cancelled = FixtureHook("on_job_cancelled", [str], None)

__all__ = [
    "on_start",
    "on_exit",
    "on_redis_connect",
    "on_init",
    "on_load_config",
    "on_job_cancelled"
]
