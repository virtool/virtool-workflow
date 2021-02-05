import asyncio
import click

# noinspection PyUnresolvedReferences
import virtool_workflow_runtime._redis
# noinspection PyUnresolvedReferences
import virtool_workflow_runtime.config
from virtool_workflow.cli_utils import apply_config_options
from virtool_workflow.fixtures.scope import FixtureScope


async def main(**config):
    with FixtureScope() as fixtures:
        try:
            await load_config(**config, scope=fixtures)
        except Exception as error:
            ...


@apply_config_options
@click.command
def runner(**config):
    asyncio.run(main(**config))
