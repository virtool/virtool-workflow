"""Main entrypoint(s) to run virtool workflows."""
import logging
from contextlib import asynccontextmanager, suppress
from importlib import import_module
from pathlib import Path

import fixtures
from virtool_workflow import Workflow, discovery, hooks
from virtool_workflow.execution.workflow_execution import WorkflowExecution
from virtool_workflow.runtime import status

logger = logging.getLogger(__name__)


def configure_logging():
    """Set up logging for a workflow run."""
    logging.basicConfig(level=logging.DEBUG)

    # Install coloredlogs if available.
    with suppress(ModuleNotFoundError):
        import coloredlogs
        logging.debug("Installed coloredlogs")
        coloredlogs.install(level=logging.DEBUG)


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
    hooks.on_update(status.send_status, once=True)
    hooks.on_failure(status.send_failed, once=True)
    hooks.on_cancelled(status.send_cancelled, once=True)
    hooks.on_success(status.send_complete, once=True)


async def run_workflow(workflow: Workflow, config: dict):
    """Run a workflow."""
    setup_hooks()
    async with fixtures.FixtureScope() as scope:
        scope["config"] = config
        return await WorkflowExecution(workflow, scope)


@asynccontextmanager
async def prepare_workflow(**config):
    """Prepare for a workflow run."""    
    load_scripts(Path(config["init_file"]), Path(config["fixtures_file"]))

    workflow = discovery.discover_workflow(
        Path(config["workflow_file_path"])
    )

    import_module("virtool_workflow.builtin_fixtures")

    if config["is_analysis_workflow"]:
        import_module("virtool_workflow.runtime.providers")
        import_module("virtool_workflow.analysis.fixtures")

    with fixtures.fixture_context():
        yield workflow


async def start(**config):
    """Main entrypoint for a workflow run."""
    async with prepare_workflow(**config) as workflow:
        await run_workflow(workflow, config)
