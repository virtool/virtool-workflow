"""Command Line Interface to virtool_workflow"""
import asyncio
from pathlib import Path

import click

from virtool_workflow.runtime.run import start_runtime


@click.option(
    "--sentry-dsn",
    help="DSN URL for sentry.",
    default=None,
)
@click.option(
    "--jobs-api-connection-string",
    help="The URL of the jobs API.",
    default="https://localhost:9950",
)
@click.option(
    "--redis-connection-string",
    help="The URL for connecting to Redis.",
    default="redis://localhost:6317",
)
@click.option(
    "--redis-list-name",
    help="The name of the redis list to watch for incoming jobs.",
    required=True,
)
@click.option(
    "--timeout",
    help="Maximum time to wait for an incoming job",
    default=1000,
)
@click.option(
    "--dev",
    help="Run in development mode.",
    is_flag=True,
)
@click.option(
    "--work-path",
    default="temp",
    help="The path where temporary files will be stored.",
    type=click.Path(path_type=Path),
)
@click.option(
    "--proc",
    help="The number of processes to use.",
    type=int,
    default=2,
)
@click.option(
    "--mem",
    help="The amount of memory to use in GB.",
    type=int,
    default=8,
)
@click.command()
def run_workflow(**kwargs):
    """Run a workflow."""
    asyncio.run(start_runtime(**kwargs))


def cli_main():
    """Main pip entrypoint."""
    run_workflow(auto_envvar_prefix="VT")
