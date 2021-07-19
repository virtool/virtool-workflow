"""Main entrypoint(s) to run virtool workflows."""
import logging
import fixtures
import warnings
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from virtool_workflow import discovery, FixtureScope
from virtool_workflow.config.fixtures import options
from virtool_workflow.hooks import on_finalize
from virtool_workflow.runtime.fixtures import runtime as runtime_fixtures
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


@asynccontextmanager
async def prepare_environment(**config):
    warnings.warn("Old runtime start called.")
    configure_logging(config.get("dev_mode", False))
    load_scripts(config["init_file"], config["fixtures_file"])

    scope = FixtureScope(options)
    scope["workflow"] = discovery.discover_workflow(
        config["workflow_file_path"])

    scope.add_provider(runtime_fixtures)

    environment = await scope.get_or_instantiate("environment")
    workflow = scope["workflow"]
    environment["workflow"] = workflow

    async with environment:
        yield environment, workflow
        await on_finalize.trigger(environment)


async def workflow_main(**config):
    """Main entrypoint for a workflow run."""
    configure_logging(config["dev_mode"])
    load_scripts(config["init_file"], config["fixtures_file"])

    workflow = discovery.discover_workflow(
        config["workflow_file_path"]
    )

    with fixtures.fixture_context():
        async with fixtures.FixtureScope() as scope:
            return await WorkflowExecution(workflow, scope)


async def start(**config):
    warnings.warn("Old runtime start called.")
    async with prepare_environment(**config) as (environment, workflow):
        await environment.execute(workflow)
