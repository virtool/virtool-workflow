"""Command Line Interface to virtool_workflow"""
import asyncio
import click

from virtool_workflow.runtime import runtime
from virtool_workflow.config.fixtures import options


@click.group()
def cli():
    ...


async def _run(**kwargs):
    await runtime.start(**kwargs)


@options.add_options
@cli.command()
def run(**kwargs):
    """Run a workflow."""
    asyncio.run(_run(**kwargs))


def cli_main():
    """Main pip entrypoint."""
    cli()
