from pathlib import Path

import pytest

pytest_plugins = [
    "tests.virtool_workflow.fixtures.workflow",
    "tests.virtool_workflow.fixtures.execution",
    "tests.standalone_runner.fixtures",
    "tests.virtool_workflow.api.fixtures",
    "virtool_workflow.testing",
]


def pytest_addoption(parser):
    parser.addoption("--db-connection-string", action="store", default="mongodb://localhost:27017")


@pytest.fixture
def db_connection_string(pytestconfig):
    return pytestconfig.getoption("db_connection_string")


@pytest.fixture
def files() -> Path:
    return Path(__file__).parent / "files"


@pytest.fixture
def analysis_files(files) -> Path:
    return files / "analysis"
