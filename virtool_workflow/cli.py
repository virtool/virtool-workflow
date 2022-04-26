"""Command Line Interface to virtool_workflow"""
import asyncio

import click

from virtool_workflow._runtime import start_runtime


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
    type=click.Path(),
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
@click.option(
    "--workflow-file",
    "-f",
    type=click.Path(exists=True),
    default="workflow.py",
    help="The path to the workflow file.",
)
@click.option(
    "--init-file",
    help="The path to the init file.",
    type=click.Path(),
    default="init.py",
)
@click.option(
    "--fixtures-file",
    help="The path to the fixtures file.",
    type=click.Path(),
    default="fixtures.py",
)
@click.command()
def run_workflow(**kwargs):
    """Run a workflow."""
    asyncio.run(start_runtime(**kwargs))


def cli_main():
    """Main pip entrypoint."""
    run_workflow(auto_envvar_prefix="VT")
