"""Command Line Interface to virtool_workflow"""
import click
import virtool_core
import virtool_workflow

@click.command()
def cli_main():
    click.echo(virtool_workflow.Workflow)