"""Main entrypoint(s) to run virtool workflows."""
import logging
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from virtool_workflow import discovery, FixtureScope
from virtool_workflow.config.loading import load_config
from virtool_workflow.config.fixtures import options
from virtool_workflow.hooks import on_load_config, on_finalize
from virtool_workflow.runtime import fixtures

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
    configure_logging(config.get("dev_mode", False))
    load_scripts(config["init_file"], config["fixtures_file"])

    scope = FixtureScope(options)
    scope["workflow"] = discovery.discover_workflow(
        config["workflow_file_path"])
    scope.add_provider(fixtures.runtime)

    environment = await scope.get_or_instantiate("environment")
    workflow = scope["workflow"]
    environment["workflow"] = workflow

    async with environment:
        yield environment, workflow
        await on_finalize.trigger(environment)


async def start(**config):
    async with prepare_environment(**config) as (environment, workflow):
        await environment.execute(workflow)
