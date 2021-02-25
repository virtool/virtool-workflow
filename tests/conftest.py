pytest_plugins = [
    "tests.virtool_workflow.fixtures.workflow",
    "tests.virtool_workflow.fixtures.execution",
    "tests.standalone_runner.fixtures",
    "tests.fixtures.db"
    "virtool_workflow.testing"
]


def pytest_addoption(parser):
    parser.add_option("--db-connection-string", action="store", default="mongodb://localhost:27017")
