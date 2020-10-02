"""Command Line Interface to virtool_workflow"""
import click
from pathlib import Path

from virtool_workflow.execute import execute

from . import discovery


@click.group()
def cli(): pass


@click.option("-f", default="workflow.py", help="python module conatianing an instance of `virtool_workflow.Workflow`")
@cli.command()
def run(f: str):
    await execute(discovery.discover_workflow(Path(f)))



def cli_main():
    cli()