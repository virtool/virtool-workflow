"""Command Line Interface to virtool_workflow"""
import asyncio
import click

from virtool_workflow import runtime
from virtool_workflow.cli_utils import apply_config_options


@click.group()
def cli():
    pass


async def _run(**kwargs):
    await runtime.start(**kwargs)


@apply_config_options
@cli.command()
def run(**kwargs):
    """Run a workflow."""
    asyncio.run(_run(**kwargs))


def cli_main():
    """Main pip entrypoint."""
    cli()
