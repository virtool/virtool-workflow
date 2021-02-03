"""Command Line Interface to virtool_workflow"""
import asyncio
import click

from virtool_workflow import runtime
from virtool_workflow.config.configuration import load_config, options


@click.group()
def cli():
    pass


def apply_config_options(func):
    for option in options:
        func = click.option(option.name, type=option.type, help=option.help)(func)

    return func


async def _run(**kwargs):
    await load_config(**kwargs)
    await runtime.start()


@apply_config_options
@cli.command()
def run(**kwargs):
    """Run a workflow."""
    asyncio.run(_run(**kwargs))


async def _print_config(**kwargs):
    config = await load_config(**kwargs)

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
