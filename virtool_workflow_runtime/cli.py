"""Command Line Interface to virtool_workflow"""
import asyncio
from pathlib import Path

import click
import uvloop

from virtool_workflow.execute_workflow import execute
from . import discovery
from . import runtime

from virtool_workflow_runtime.config.configuration import VirtoolConfiguration
from virtool_workflow_runtime.config import fixtures

JOB_ID_ENV = "VIRTOOL_JOB_ID"


@click.group()
def cli():
    """Main cli entrypoint."""
    uvloop.install()


def create_config(**kwargs):
    return VirtoolConfiguration(
        data_path=kwargs["data_path"] or fixtures.data_path_str(),
        temp_path=kwargs["temp_path"] or fixtures.temp_path_str(),
        proc=kwargs["proc"] or fixtures.proc(),
        mem=kwargs["mem"] or fixtures.mem(),
        redis_connection_string=kwargs["redis_connection_string"] or fixtures.redis_connection_string(),
        no_sentry=kwargs["no_sentry"] if kwargs["no_sentry"] is not None else fixtures.no_sentry(),
        development_mode=kwargs["dev"] if kwargs["dev"] is not None else fixtures.dev_mode(),
        mongo_database_name=kwargs["db_name"] or fixtures.db_name(),
        mongo_connection_string=kwargs["db_connection_string"] or fixtures.db_connection_string(),
    )


def apply_config_options(func):

    func = click.option("--temp-path", type=click.Path())(func)
    func = click.option("--proc", type=int)(func)
    func = click.option("--mem", type=int)(func)
    func = click.option("--redis-connection-string", type=str)(func)
    func = click.option("--no-sentry", type=bool)(func)
    func = click.option("--dev", type=bool)(func)
    func = click.option("--db-name", type=str)(func)
    func = click.option("--db-connection-string", type=str)(func)
    func = click.option("--data-path", type=click.Path())(func)

    return func


def workflow_file_option(func):
    """Option to provide workflow file."""
    return click.option(
        "-f",
        default="workflow.py",
        type=click.Path(exists=True),
        help="python module containing an instance of `virtool_workflow.Workflow`"
    )(func)


@apply_config_options
@workflow_file_option
@click.argument("job_id", nargs=1, envvar=JOB_ID_ENV)
@cli.command()
def run(f: str, job_id: str, **kwargs):
    """Run a workflow and send updates to Virtool."""
    workflow, _ = discovery.run_discovery(Path(f), Path(f).parent / "fixtures.py")
    config = create_config(**kwargs)
    asyncio.run(runtime.execute(job_id, workflow, config=config))


@apply_config_options
@workflow_file_option
@cli.command()
def run_local(f: str, **kwargs):
    """Run a workflow locally, without runtime specific dependencies."""
    config = create_config(**kwargs)
    asyncio.run(execute(discovery.discover_workflow(Path(f).absolute()), config=config))


def cli_main():
    """Main pip entrypoint."""
    cli()
