import asyncio
import click

# noinspection PyUnresolvedReferences
import virtool_workflow_runtime._redis
# noinspection PyUnresolvedReferences
import virtool_workflow_runtime.config
from virtool_workflow.cli_utils import apply_config_options
from virtool_workflow.config.configuration import load_config
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow_runtime import hooks

runner_scope = FixtureScope()


async def main(**config):
    with runner_scope as fixtures:
        try:
            await load_config(**config, scope=fixtures)
        except Exception as error:
            fixtures["error"] = error
        finally:
            await hooks.on_exit.trigger(fixtures)


@apply_config_options
@click.command
def runner(**config):
    asyncio.run(main(**config))
