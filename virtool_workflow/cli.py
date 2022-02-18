"""Command Line Interface to virtool_workflow"""
import asyncio

import click

from virtool_workflow.options import apply_options
from virtool_workflow.runtime import runtime
from virtool_workflow.runtime.redis import run_jobs_from_redis, run_job_from_redis
from virtool_workflow.testing.cli import test_main


@click.group()
def cli():
    runtime.configure_logging()
    ...


@apply_options
@click.argument("job_id")
@cli.command()
def run(job_id, **kwargs):
    """Run a workflow."""
    asyncio.run(runtime.start(job_id=job_id, **kwargs))


@click.option(
    "--exit-after-one",
    is_flag=True,
    help="Exit after running a single job from redis.",
)
@click.option(
    "--redis-url",
    default="redis://localhost:6317",
)
@apply_options
@click.argument("list_name")
@cli.command()
def run_from_redis(exit_after_one, **kwargs):
    """Run jobs from redis for a workflow."""
    asyncio.run(
        run_job_from_redis(**kwargs)
        if exit_after_one is True
        else run_jobs_from_redis(**kwargs)
    )


def cli_main(**kwargs):
    """Main pip entrypoint."""
    cli.command("test")(test_main)
    cli(auto_envvar_prefix="VT")
