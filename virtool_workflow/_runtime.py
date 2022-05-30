import asyncio
import logging
import os
import signal
import sys
from contextlib import suppress
from importlib import import_module
from pathlib import Path
from typing import Any, Dict

from pyfixtures import FixtureScope, runs_in_new_fixture_context
from virtool_workflow import discovery, execute
from virtool_workflow.events import Events
from virtool_workflow.hooks import (
    on_failure,
    on_cancelled,
    on_success,
    on_step_start,
    on_terminated,
    on_error,
)
from virtool_workflow.redis import (
    configure_redis,
    get_next_job_with_timeout,
    wait_for_cancellation,
)
from virtool_workflow.sentry import configure_sentry
from virtool_workflow.workflow import Workflow

logger = logging.getLogger(__name__)


def configure_logging(level: int):
    """Set the log level and configure logging."""
    logging.basicConfig(level=level)

    # Use coloredlogs if installed
    with suppress(ModuleNotFoundError):
        coloredlogs = import_module("coloredlogs")
        logging.debug("Installed coloredlogs")
        coloredlogs.install(level=level)


def configure_workflow(
    fixtures_file: os.PathLike,
    init_file: os.PathLike,
    workflow_file: os.PathLike,
):
    logger.info("Importing workflow")
    workflow = discovery.discover_workflow(Path(workflow_file))

    logger.info("Importing additional files")
    for f in (Path(f) for f in (init_file, fixtures_file)):
        try:
            module = discovery.import_module_from_file(f.name.rstrip(".py"), f)
            logger.info(f"Imported {module}")
        except FileNotFoundError:
            if init_file != "init.py" or fixtures_file != "fixtures.py":
                raise

    for name in (
        "virtool_workflow.builtin_fixtures",
        "virtool_workflow.analysis.fixtures",
        "virtool_workflow.runtime.providers",
    ):
        module = import_module(name)
        logger.debug(f"Imported {module}")

    return workflow


def configure_builtin_status_hooks():
    """
    Configure built-in job status hooks.

    Push status updates to API when various lifecycle hooks are triggered.

    """

    @on_step_start
    async def handle_step_start(push_status):
        await push_status(state="running")

    @on_error(once=True)
    async def handle_error(error, push_status):
        await push_status(
            stage="",
            state="error",
            error=error,
            max_tb=50,
        )

    @on_cancelled(once=True)
    async def handle_cancelled(push_status):
        await push_status(stage="", state="cancelled")

    @on_terminated
    async def handle_terminated(push_status):
        await push_status(stage="", state="terminated")

    @on_success(once=True)
    async def handle_success(push_status):
        await push_status(stage="", state="complete")


def cleanup_builtin_status_hooks():
    """
    Clear callbacks for built-in status hooks.

    This prevents carryover of hooks between tests. Carryover won't be encountered in
    production because workflow processes exit after one run.

    TODO: Find a better way to isolate hooks to workflow runs.

    """
    on_step_start.clear()
    on_failure.clear()
    on_cancelled.clear()
    on_success.clear()
    on_error.clear()
    on_terminated.clear()


async def run_workflow(
    config: Dict[str, Any],
    job_id: str,
    workflow: Workflow,
    events: Events,
) -> Dict[str, Any]:
    # Configure hooks here so that they can be tested when using `run_workflow`.
    configure_builtin_status_hooks()

    async with FixtureScope() as scope:
        scope["config"] = config
        scope["job_id"] = job_id

        execute_task = asyncio.create_task(execute(workflow, scope, events))

        try:
            await execute_task
        except asyncio.CancelledError:
            execute_task.cancel()

        await execute_task

        cleanup_builtin_status_hooks()

        return scope.get("results", {})


@runs_in_new_fixture_context()
async def start_runtime(
    dev: bool,
    fixtures_file: os.PathLike,
    init_file: os.PathLike,
    jobs_api_connection_string: str,
    mem: int,
    proc: int,
    redis_connection_string: str,
    redis_list_name: str,
    timeout: int,
    sentry_dsn: str,
    work_path: os.PathLike,
    workflow_file: os.PathLike,
):
    log_level = logging.DEBUG if dev else logging.INFO
    configure_logging(log_level)
    configure_sentry(sentry_dsn, log_level)

    workflow = configure_workflow(fixtures_file, init_file, workflow_file)

    config = dict(
        dev=dev,
        jobs_api_connection_string=jobs_api_connection_string,
        mem=mem,
        proc=proc,
        work_path=work_path,
    )

    async with configure_redis(redis_connection_string, timeout=15) as redis:
        try:
            job_id = await get_next_job_with_timeout(redis_list_name, redis, timeout)
        except asyncio.TimeoutError:
            # This happens due to Kubernetes scheduling issues or job cancellations. It
            # is not an error.
            logging.warning("Timed out while waiting for job")
            sys.exit(0)

    events = Events()

    workflow_run = asyncio.create_task(run_workflow(config, job_id, workflow, events))

    def terminate_workflow(*_):
        events.terminated.set()
        workflow_run.cancel()

    signal.signal(signal.SIGTERM, terminate_workflow)

    def cancel_workflow(*_):
        events.cancelled.set()
        workflow_run.cancel()

    async with configure_redis(redis_connection_string, timeout=15) as redis:
        cancellation_task = asyncio.create_task(
            wait_for_cancellation(redis, job_id, cancel_workflow)
        )

        await workflow_run

        cancellation_task.cancel()
        await cancellation_task

    if events.terminated.is_set():
        sys.exit(124)
