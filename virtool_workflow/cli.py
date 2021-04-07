"""Command Line Interface to virtool_workflow"""
import asyncio
import click

from virtool_workflow import runtime
from virtool_workflow.config.fixtures import options


@options.add_options
@click.group()
@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj = kwargs


async def _run(**kwargs):
    await runtime.start(**kwargs)


@cli.command()
@click.pass_obj
def run(obj, **kwargs):
    """Run a workflow."""
    asyncio.run(_run(**obj, **kwargs))


def cli_main():
    """Main pip entrypoint."""
    cli()
