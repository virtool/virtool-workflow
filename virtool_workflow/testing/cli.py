import os
import sys
from pathlib import Path
from shutil import which
from subprocess import PIPE, Popen

from virtool_workflow.config.fixtures import options

API_COMPOSE_FILE = Path(__file__).parent/"docker-compose.api.yml"
WORKFLOW_COMPOSE_FILE = Path(__file__).parent/"docker-compose.workflow.yml"
COMPOSE_FILE = f"{API_COMPOSE_FILE.absolute()}:{WORKFLOW_COMPOSE_FILE.absolute()}"


@options.add_options
def test_main(**kwargs):
    """Run a workflow in a test environment"""

    if which("docker-compose") is None:
        raise RuntimeError("docker-compose is not installed.")

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
            "VT_ADD_ARGS": " ".join(sys.argv[2:]),
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
