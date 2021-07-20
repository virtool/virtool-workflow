"""Command Line Interface to virtool_workflow"""
import asyncio
import click

from virtool_workflow.runtime import runtime
from virtool_workflow.testing.cli import test_main
from virtool_workflow.options import apply_options


@click.group()
def cli():
    ...


async def _run(**kwargs):
    await runtime.start(**kwargs)


@apply_options
@cli.command()
def run(job_id, **kwargs):
    """Run a workflow."""
    asyncio.run(_run(job_id=job_id, **kwargs))


def cli_main():
    """Main pip entrypoint."""
    cli.command("test")(test_main)
    cli()
