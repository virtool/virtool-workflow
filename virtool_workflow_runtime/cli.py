import asyncio
import logging

import click

# noinspection PyUnresolvedReferences
import virtool_workflow_runtime._docker

# noinspection PyUnresolvedReferences
import virtool_workflow_runtime._docker_events

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
from virtool_workflow.config.configuration import load_config
from virtool_workflow.config.fixtures import options
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow_runtime import hooks
from virtool_workflow_runtime.job_loop import job_loop

logger = logging.getLogger()
runner_scope = FixtureScope()


async def init(fixtures, **config):
    """Run initialization tasks before processing jobs."""
    await hooks.on_init.trigger(fixtures)
    await load_config(**config, hook=hooks.on_load_config, scope=fixtures)
    await hooks.on_start.trigger(fixtures)


async def main(**config):
    """The main entrypoint for the standalone workflow runner."""
    async with runner_scope as fixtures:
        fixtures["error"] = None
        try:
            await init(fixtures, **config)

            loop = await fixtures.bind(job_loop)
            fixtures["tasks"]["job_loop"] = asyncio.create_task(loop())

            await asyncio.gather(fixtures["tasks"]["job_loop"])

        except Exception as error:
            fixtures["error"] = error
        finally:
            await hooks.on_exit.trigger(
                fixtures, suppress=isinstance(fixtures["error"], Exception)
            )

            if fixtures["error"]:
                raise fixtures["error"]


@options.add_options
@click.command
def runner(**config):
    asyncio.run(main(**config))
