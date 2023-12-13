pytest_plugins = [
    "tests.fixtures",
    "tests.fixtures.api",
    "tests.fixtures.data",
    "tests.fixtures.execution",
    "tests.fixtures.redis",
    "tests.fixtures.scope",
]


def pytest_addoption(parser):
    parser.addoption(
        "--redis-connection-string",
        action="store",
        default="redis://root:virtool@localhost:9004",
    )
