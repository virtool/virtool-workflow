"""Command Line Interface to virtool_workflow"""
from pathlib import Path

import click
import uvloop

from virtool_workflow.execute_workflow import execute
from . import discovery
from . import runtime

JOB_ID_ENV = "VIRTOOL_JOB_ID"


@click.group()
def cli():
    """Main cli entrypoint."""
    uvloop.install()


def workflow_file_option(func):
    """Option to provide workflow file."""
    return click.option(
        func,
        "-f",
        default="workflow.py",
        type=click.Path(exists=True),
        help="python module containing an instance of `virtool_workflow.Workflow`"
    )


@workflow_file_option
@click.argument("job_id", nargs=1, envvar=JOB_ID_ENV)
@cli.command()
async def run(file: str, job_id: str):
    """Run a workflow and send updates to Virtool."""
    workflow, _ = discovery.run_discovery(Path(file), Path(file).parent / "fixtures.py")

    await runtime.execute(job_id, workflow)


@workflow_file_option
@cli.command()
async def run_local(f: str):
    """Run a workflow locally, without runtime specific dependencies."""
    await execute(discovery.discover_workflow(Path(f).absolute()))


def cli_main():
    """Main pip entrypoint."""
    cli()
