pytest_plugins = [
    "tests.fixtures",
    "tests.fixtures.api",
    "tests.fixtures.execution",
    "tests.fixtures.redis",
    "tests.fixtures.scope",
    "virtool_workflow.pytest_plugin",
]


def pytest_addoption(parser):
    parser.addoption(
        "--redis-connection-string",
        action="store",
        default="redis://root:virtool@localhost:9004",
    )
