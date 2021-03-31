"""Command Line Interface to virtool_workflow"""
import asyncio
import click

from virtool_workflow import runtime
from virtool_workflow.config.fixtures import options


@options.add_options
@click.group()
def cli():
    pass


async def _run(**kwargs):
    await runtime.start(**kwargs)


@cli.command()
def run(**kwargs):
    """Run a workflow."""
    asyncio.run(_run(**kwargs))


def cli_main():
    """Main pip entrypoint."""
    cli()
