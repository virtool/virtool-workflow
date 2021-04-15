from pathlib import Path

import pytest

pytest_plugins = [
    "tests.virtool_workflow.fixtures.workflow",
    "tests.virtool_workflow.fixtures.execution",
    "tests.standalone_runner.fixtures", "tests.virtool_workflow.api.fixtures",
    "virtool_workflow.testing"
]


def pytest_addoption(parser):
    parser.addoption("--db-connection-string",
                     action="store",
                     default="mongodb://localhost:27017")


@pytest.fixture
def db_connection_string(pytestconfig):
    return pytestconfig.getoption("db_connection_string")


TEST_FILES_DIR = Path(__file__).parent / "files"
ANALYSIS_TEST_FILES_DIR = TEST_FILES_DIR / "analysis"


@pytest.fixture
def files() -> Path:
    return TEST_FILES_DIR


@pytest.fixture
def analysis_files() -> Path:
    return ANALYSIS_TEST_FILES_DIR


@pytest.fixture
def work_path(tmpdir):
    return Path(tmpdir)


@pytest.fixture(scope="session")
def docker_compose_files(pytestconfig):
    return [str(Path(__file__).parent / "docker-compose.pytest.yml")]


@pytest.fixture(scope="session", autouse=True)
def redis_url(docker_services):
    docker_services.start('redis')
    return f"redis://{docker_services.docker_ip}:6379"


@pytest.fixture(scope="session")
def real_jobs_api_url(docker_services):
    docker_services.start('job-api')
    port = docker_services.wait_for_service("job-api", 9990)
    return f"http://{docker_services.docker_ip}:{port}/api"
