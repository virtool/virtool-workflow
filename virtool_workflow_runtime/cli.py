import asyncio
import click
import logging

# noinspection PyUnresolvedReferences
import virtool_workflow_runtime._docker
# noinspection PyUnresolvedReferences
import virtool_workflow_runtime._redis
# noinspection PyUnresolvedReferences
import virtool_workflow_runtime.cancellations
# noinspection PyUnresolvedReferences
import virtool_workflow_runtime.config
# noinspection PyUnresolvedReferences
import virtool_workflow_runtime.new_jobs
# noinspection PyUnresolvedReferences
import virtool_workflow_runtime.on_init
from virtool_workflow.cli_utils import apply_config_options
from virtool_workflow.config.configuration import load_config
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow_runtime import hooks

logger = logging.getLogger()
runner_scope = FixtureScope()


async def job_loop(jobs):
    """Process incoming jobs."""
    async for job in jobs:
        logger.debug(f"Processing job {job}")
        ...


async def init(fixtures, **config):
    """Run initialization tasks before processing jobs."""
    await hooks.on_init.trigger(fixtures)
    await load_config(**config, hook=hooks.on_load_config, scope=fixtures)
    await hooks.on_start.trigger(fixtures)


async def main(**config):
    """The main entrypoint for the standalone workflow runner."""
    with runner_scope as fixtures:
        fixtures["error"] = None
        try:
            await init(fixtures, **config)

            loop = await fixtures.bind(job_loop)
            await loop()

        except Exception as error:
            fixtures["error"] = error
            raise error
        finally:
            await hooks.on_exit.trigger(fixtures)


@apply_config_options
@click.command
def runner(**config):
    asyncio.run(main(**config))
