"""Main entrypoint(s) to run virtool workflows."""
from contextlib import asynccontextmanager
from importlib import import_module
from logging import getLogger
from pathlib import Path

import pyfixtures

from virtool_workflow import Workflow, discovery, hooks
from virtool_workflow._executor import execute
from virtool_workflow.runtime import status

logger = getLogger(__name__)


def load_scripts(init_file: Path, fixtures_file: Path):
    """Load the initialization and fixtures scripts."""
    if init_file.exists():
        discovery.import_module_from_file(
            module_name=init_file.name.rstrip(".py"), path=init_file
        )
    if fixtures_file.exists():
        discovery.import_module_from_file(
            module_name=fixtures_file.name.rstrip(".py"), path=fixtures_file
        )


def setup_hooks():
    """Add hooks for a workflow run."""
    hooks.on_step_start(status.send_status)
    hooks.on_failure(status.send_failed, once=True)
    hooks.on_cancelled(status.send_cancelled, once=True)
    hooks.on_success(status.send_complete, once=True)


async def run_workflow(workflow: Workflow, config: dict):
    """Run a workflow."""
    setup_hooks()
    async with pyfixtures.FixtureScope() as scope:
        scope["config"] = config
        await execute(workflow, scope)
        return scope["results"] if "results" in scope else {}


@asynccontextmanager
async def prepare_workflow(**config):
    """Prepare for a workflow run."""
    if config["sentry_dsn"] is not None:
        import virtool_workflow.sentry

        virtool_workflow.sentry.sentry_init(config["sentry_dsn"], config["dev_mode"])

    load_scripts(Path(config["init_file"]), Path(config["fixtures_file"]))

    workflow = discovery.discover_workflow(Path(config["workflow_file_path"]))

    import_module("virtool_workflow.builtin_fixtures")

    if config["is_analysis_workflow"]:
        import_module("virtool_workflow.runtime.providers")
        import_module("virtool_workflow.analysis.fixtures")

    with pyfixtures.fixture_context():
        yield workflow


async def start(**config):
    """Main entrypoint for a workflow run."""
    async with prepare_workflow(**config) as workflow:
        await run_workflow(workflow, config)
