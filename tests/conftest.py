from pathlib import Path

import pytest

pytest_plugins = [
    "tests.virtool_workflow.fixtures.workflow",
    "tests.virtool_workflow.fixtures.execution",
    "tests.virtool_workflow.api.fixtures",
    "virtool_workflow.testing.fixtures",
]


def pytest_addoption(parser):
    parser.addoption("--db-connection-string", action="store", default="mongodb://localhost:27017")


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
