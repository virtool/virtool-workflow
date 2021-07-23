import os
import sys
import click
import yaml
from pathlib import Path
from shutil import which
from subprocess import PIPE, Popen

from virtool_workflow.options import apply_options

API_COMPOSE_FILE = Path(__file__).parent/"docker-compose.api.yml"
WORKFLOW_COMPOSE_FILE = Path(__file__).parent/"docker-compose.workflow.yml"
COMPOSE_FILE = f"{API_COMPOSE_FILE.absolute()}:{WORKFLOW_COMPOSE_FILE.absolute()}"


@click.option(
    "--job-id",
    help="Job ID to use for the workflow run.",
    default=None,
)
@apply_options
def test_main(job_id, **kwargs):
    """Run a workflow in a test environment"""

    if job_id is None:
        with open("test_case.yml", "r") as test_case_yml:
            yml = yaml.safe_load(test_case_yml)
            job_id = yml["job_id"]

    if which("docker-compose") is None:
        raise RuntimeError("docker-compose is not installed.")

    run_args = [job_id] + sys.argv[2:]

    proc = Popen(
        [
            "docker-compose",
            "up",
            "--build",
            "--abort-on-container-exit",
            "--force-recreate",
            "--exit-code-from",
            "workflow"
        ],
        stdout=PIPE,
        stderr=PIPE,
        env={
            "VT_ADD_ARGS": " ".join(run_args),
            "COMPOSE_FILE": COMPOSE_FILE,
            "WORKFLOW_DIR": os.getcwd(),
            **os.environ,
        },
    )

    for line in (str(line, encoding="utf-8") for line in proc.stdout):
        print(line.strip())

    for line in (str(line, encoding="utf-8") for line in proc.stderr):
        print(line.strip())

    proc.communicate()

    exit(proc.returncode)
