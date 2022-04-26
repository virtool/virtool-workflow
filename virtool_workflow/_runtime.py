import asyncio
import logging
import os
from contextlib import suppress
from importlib import import_module
from pathlib import Path
from typing import Any, Dict

from fixtures import FixtureScope, runs_in_new_fixture_context
from virtool_workflow import discovery, execute
from virtool_workflow.execution.hooks.workflow_hooks import on_step_start
from virtool_workflow.hooks import on_failure, on_cancelled, on_success
from virtool_workflow.redis import configure_redis, get_next_job
from virtool_workflow.sentry import configure_sentry
from virtool_workflow.signals import configure_signal_handling
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
        "virtool_workflow.analysis.fixtures"
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
    async def send_status(push_status):
        await push_status(state="running")

    @on_failure(once=True)
    async def send_failed(error, push_status):
        await push_status(
            stage="",
            state="error",
            error=error,
            max_tb=50,
        )

    @on_cancelled(once=True)
    async def send_cancelled(push_status):
        await push_status(state="cancelled")

    @on_success(once=True)
    async def send_complete(push_status):
        await push_status(state="complete", stage="completed")


async def run_workflow(
    config: Dict[str, Any],
    job_id: str,
    workflow: Workflow
) -> Dict[str, Any]:
    # Configure hooks here so that they can be tested when using `run_workflow`.
    configure_builtin_status_hooks()

    async with FixtureScope() as scope:
        scope["config"] = config
        scope["job_id"] = job_id
        await execute(workflow, scope)
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
    configure_signal_handling()

    workflow = configure_workflow(fixtures_file, init_file, workflow_file)

    config = dict(
        dev=dev,
        jobs_api_connection_string=jobs_api_connection_string,
        mem=mem,
        proc=proc,
        work_path=work_path,
    )

    async with configure_redis(redis_connection_string) as redis:
        job_id = await get_next_job(redis_list_name, redis, timeout=timeout)

    workflow_run = asyncio.create_task(
        run_workflow(config, job_id, workflow)
    )

    await workflow_run
