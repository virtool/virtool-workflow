import asyncio
import click

# noinspection PyUnresolvedReferences
import virtool_workflow_runtime._redis
# noinspection PyUnresolvedReferences
import virtool_workflow_runtime.config
from virtool_workflow.cli_utils import apply_config_options
from virtool_workflow.config.configuration import load_config


async def main(**config):
    await load_config(**config)


@apply_config_options
@click.command
def runner(**config):
    asyncio.run(main(**config))
