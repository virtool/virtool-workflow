from pathlib import Path

import pytest

pytest_plugins = [
    "docker_compose",
    "tests.api.fixtures",
    "tests.fixtures.execution",
    "tests.fixtures.workflow",
    "tests.integration._fixtures.containers",
    "tests.integration._fixtures.db",
    "tests.integration._fixtures.jobs",
    "tests.integration._fixtures.workflows",
    "tests.integration._fixtures.redis",
    "virtool_workflow.testing.fixtures",
]


def pytest_addoption(parser):
    parser.addoption("--redis-url", action="store", default="redis://localhost:6379")


@pytest.fixture
def redis_url(pytestconfig):
    return pytestconfig.getoption("redis_url")


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
