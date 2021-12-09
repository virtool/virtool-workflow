from typing import List

import click

options = [
    click.option(
        "--work-path",
        default="temp",
        help="The path where temporary files will be stored.",
        type=click.Path()
    ),
    click.option(
        "--proc",
        help="The number of processes to use.",
        type=int,
        default=2,
    ),
    click.option(
        "--mem",
        help="The amount of memory to use in GB.",
        type=int,
        default=8,
    ),
    click.option(
        "--dev-mode",
        help="Run in development mode.",
        is_flag=True,
    ),
    click.option(
        "--jobs-api-url",
        help="The URL of the jobs API.",
        default="https://localhost:9950",
    ),
    click.option(
        "--is-analysis-workflow",
        help="The workflow is an analysis workflow.",
        is_flag=True
    ),
    click.option(
        "--workflow-file-path",
        type=click.Path(exists=True),
        default="workflow.py",
        help="The path to the workflow file.",
    ),
    click.option(
        "--init-file",
        help="The path to the init file.",
        type=click.Path(),
        default="init.py"
    ),
    click.option(
        "--fixtures-file",
        help="The path to the fixtures file.",
        type=click.Path(),
        default="fixtures.py"
    ),
]


def apply_options(func, _options: List[click.Option] = None):
    """Apply click options from a list."""
    if _options is None:
        _options = options
    for option in options:
        func = option(func)
    return func
