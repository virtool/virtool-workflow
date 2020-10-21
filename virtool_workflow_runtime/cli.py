"""Command Line Interface to virtool_workflow"""
import click
import uvloop
from pathlib import Path

from virtool_workflow.execute_workflow import execute
from . import runtime

from . import discovery

JOB_ID_ENV = "VIRTOOL_JOB_ID"


@click.group()
def cli():
    uvloop.install()


def workflow_file_option(func):
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
async def run(f: str, job_id: str):
    workflow, _ = discovery.run_discovery(Path(f), Path(f).parent/"fixtures.py")

    await runtime.execute(workflow, job_id=job_id)


@workflow_file_option
@cli.command()
async def run_local(f: str):
    await execute(discovery.discover_workflow(Path(f).absolute()))


def cli_main():
    cli()
