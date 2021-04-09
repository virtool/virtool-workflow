import tempfile
from pathlib import Path

import click

from .utils import DONE, bcolors, clone, color, docker_build

JOBS_API_DOCKERFILE = Path(__file__).parent / "api-server-Dockerfile"
WORKFLOW_DOCKER_FILE = Path(__file__).parent / "latest-workflow-local-Dockerfile"
INTEGRATION_WORKFLOW_DOCKER_FILE = Path(__file__).parent / "workflow/Dockerfile"


@click.group()
def cli():
    ...


@cli.group()
def build():
    """Build the required docker images with the latest version of the code."""
    ...


@click.option(
    "--path",
    default="..",
    type=click.Path(),
    help="The path to a local clone of the virtool-workflow git repository.",
)
@click.option(
    "--remote", default=None, help="The virtool-workflow git repository to pull from."
)
@build.command()
def workflow(path, remote):
    """Build the `virtool/workflow` image."""
    tag = "virtool/workflow"
    if remote is not None:
        tempd = tempfile.mkdtemp()
        print(color(bcolors.OKBLUE, f"Created temporary directory {tempd}..."))
        print(color(bcolors.OKBLUE, f"Cloning {remote}...\n"))
        clone(remote, cwd=tempd)
        context = Path(tempd) / "virtool-workflow"
    else:
        context = path

    print(color(bcolors.OKBLUE, f"\nBuilding `{color(bcolors.OKGREEN, tag)}`...\n"))
    docker_build(
        dockerfile=WORKFLOW_DOCKER_FILE, context=context, tag=tag,
    )


@build.command()
def integration():
    """Build the `virtool/integration_test_workflow` image."""
    tag = "virtool/integration_test_workflow"
    print(color(bcolors.OKBLUE, f"\nBuilding `{color(bcolors.OKGREEN, tag)}`...\n"))
    docker_build(
        dockerfile=INTEGRATION_WORKFLOW_DOCKER_FILE,
        context=Path(__file__).parent / "workflow",
        tag=tag,
    )
    print(DONE)


@click.option(
    "--remote",
    default="https://github.com/virtool/virtool",
    help="The virtool git repository to pull from.",
)
@click.option(
    "--path",
    default=None,
    help="The path to a local clone of the virtool git repository.",
)
@build.command()
def jobs_api(path, remote):
    """Build the `virtool/jobs-api` image."""
    tag = "virtool/jobs-api"
    if path is None:
        tempd = tempfile.mkdtemp()
        print(color(bcolors.OKBLUE, f"Created temporary directory {tempd}..."))
        print(color(bcolors.OKBLUE, f"Cloning {remote}...\n"))
        clone(remote, cwd=tempd)

        context = Path(tempd) / "virtool"
    else:
        context = path

    print(color(bcolors.OKBLUE, f"\nBuilding `{color(bcolors.OKGREEN, tag)}`...\n"))

    docker_build(
        dockerfile=JOBS_API_DOCKERFILE, context=context, tag=tag,
    )

    print(DONE)


@click.option(
    "--virtool-remote",
    default="https://github.com/virtool/virtool",
    help="The virtool git repository to pull from.",
)
@click.option(
    "--virtool-path",
    default=None,
    help="The path to a local clone of the virtool git repository.",
)
@click.option(
    "--virtool-workflow-path",
    default="..",
    type=click.Path(),
    help="The path to a local clone of the virtool-workflow git repository.",
)
@click.option(
    "--virtool-workflow-remote",
    default=None,
    help="The virtool-workflow git repository to pull from.",
)
@build.command()
@click.pass_context
def all(
    ctx, virtool_remote, virtool_path, virtool_workflow_remote, virtool_workflow_path
):
    """Build all of the required images."""
    ctx.invoke(workflow, remote=virtool_workflow_remote, path=virtool_workflow_path)
    ctx.invoke(integration)
    ctx.invoke(jobs_api, remote=virtool_remote, path=virtool_path)
