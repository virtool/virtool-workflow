"""Command Line Interface to virtool_workflow"""
import asyncio
import click

from virtool_workflow import runtime
from virtool_workflow.config.configuration import options


@click.group()
def cli():
    pass


def apply_config_options(func):
    for option in options.values():
        func = click.option(option.option_name, type=option.type, help=option.help)(func)

    return func


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
