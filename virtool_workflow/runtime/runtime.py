"""Main entrypoint(s) to run virtool workflows."""
import logging
import fixtures
import warnings
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fixtures import FixtureScope
from virtool_workflow import discovery
from virtool_workflow.config.fixtures import options
from virtool_workflow.hooks import on_finalize
from virtool_workflow.execution.workflow_execution import WorkflowExecution

logger = logging.getLogger(__name__)


def configure_logging(dev_mode):
    """Set up logging for a workflow run."""
    log_level = logging.DEBUG if dev_mode else logging.INFO

    logging.basicConfig(level=log_level)
    # Install coloredlogs if available.
    with suppress(ModuleNotFoundError):
        import coloredlogs
        logging.debug("Installed coloredlogs")
        coloredlogs.install(level=log_level)


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


async def start(**config):
    """Main entrypoint for a workflow run."""
    configure_logging(config["dev_mode"])
    load_scripts(config["init_file"], config["fixtures_file"])

    workflow = discovery.discover_workflow(
        config["workflow_file_path"]
    )

    with fixtures.fixture_context():
        async with fixtures.FixtureScope() as scope:
            return await WorkflowExecution(workflow, scope)
