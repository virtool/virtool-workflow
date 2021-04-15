from pathlib import Path

import pytest

pytest_plugins = [
    "tests.virtool_workflow.fixtures.workflow",
    "tests.virtool_workflow.fixtures.execution",
    "tests.standalone_runner.fixtures", "tests.virtool_workflow.api.fixtures",
    "virtool_workflow.testing", "tests.docker_fixtures"
]


def pytest_addoption(parser):
    parser.addoption("--redis-url", action="store", default=None)
    parser.addoption("--postgres-url", action="store", default=None)
    parser.addoption("--mongo-url", action="store", default=None)


@pytest.fixture(scope="session")
def redis_url(request):
    return request.config.getoption("--redis-url")


@pytest.fixture(scope="session")
def postgres_url(request):
    return request.config.getoption("--postgres-url")


@pytest.fixture(scope="session")
def mongo_url(request):
    return request.config.getoption("--mongo-url")


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
