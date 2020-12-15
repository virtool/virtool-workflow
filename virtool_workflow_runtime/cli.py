"""Command Line Interface to virtool_workflow"""
import asyncio
from pathlib import Path

import click

from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from virtool_workflow_runtime.config.configuration import create_config, options
from . import discovery
from . import runtime

JOB_ID_ENV = "VIRTOOL_JOB_ID"


@click.group()
def cli():
    pass


def workflow_file_option(func):
    """Option to provide workflow file."""
    return click.option(
        "-f",
        default="workflow.py",
        type=click.Path(),
        help="python module containing an instance of `virtool_workflow.Workflow`"
    )(func)


def apply_config_options(func):
    for _, option_name, type_, _, help_, _ in options:
        func = click.option(option_name, type=type_, help=help_)(func)

    return func


async def _run(file: str, job_id: str, **kwargs):
    with WorkflowFixtureScope() as scope:
        config = await create_config(scope, **kwargs)
        workflow, _ = discovery.run_discovery(Path(file), Path(file).parent / "fixtures.py")

        result = await runtime.execute(workflow, runtime.DirectDatabaseAccessRuntime(job_id))
        if config.dev_mode:
            print(result)


@apply_config_options
@workflow_file_option
@click.argument("job_id", nargs=1, envvar=JOB_ID_ENV)
@cli.command()
def run(f: str, job_id: str, **kwargs):
    """Run a workflow and send updates to Virtool."""
    asyncio.run(_run(f, job_id, **kwargs))


async def _print_config(**kwargs):
    with WorkflowFixtureScope() as scope:
        config = await create_config(scope, **kwargs)

        for name, value in vars(config).items():
            print(f"{name}: {value}")


@apply_config_options
@cli.command()
def print_config(**kwargs):
    """Print the configuration which would be used with the given arguments."""
    asyncio.run(_print_config(**kwargs))


@apply_config_options
@cli.command()
def create_env_script(**kwargs):
    """Create a bash script to set environment variables based on default values and provided arguments."""
    commands = []
    for name, _, _, _, _, fixture in options:
        if name in kwargs and kwargs[name] is not None:
            commands.append(f"export {fixture.environment_variable}={kwargs[name]}")
        else:
            commands.append(f"export {fixture.environment_variable}={fixture.default_value}")
    for cmd in commands:
        print(cmd)


def cli_main():
    """Main pip entrypoint."""
    cli()
