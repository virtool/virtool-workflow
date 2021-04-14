import pytest
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def docker_compose_files(pytestconfig):
    return [str(Path(__file__).parent / "docker-compose.yml")]


@pytest.fixture(scope="session", autouse=True)
def docker(docker_services):
    docker_services.start()
