import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def docker_compose_files(pytestconfig):
    return [str(Path(__file__).parent / "docker-compose.yml")]


@pytest.fixture(scope="session")
def jobs_api_url(docker_services):
    docker_services.start('job-api')
    port = docker_services.wait_for_service("job-api", 9990)
    return f"http://{docker_services.docker_ip}:{port}/api"
