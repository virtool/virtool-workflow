import pytest
import docker as docker_py
from pathlib import Path


@pytest.fixture(scope="session")
def docker_compose_files(pytestconfig):
    return [str(Path(__file__).parent / "docker-compose.pytest.yml")]


@pytest.fixture(scope="session", autouse=True)
def redis_url(docker_services):
    docker_services.start('redis')
    return f"redis://{docker_services.docker_ip}:6379"


@pytest.fixture(scope="session", autouse=True)
def postgres_url(docker_services):
    docker_services.start('postgres')
    return ("postresql+asyncpg://virtool:virtool"
            f"@{docker_services.docker_ip}:5432/virtool")


@pytest.fixture(scope="session", autouse=True)
def mongo_url(docker_services):
    docker_services.start('postgres')
    return f"redis://{docker_services.docker_ip}:5432"


@pytest.fixture(scope="session")
def real_jobs_api_url(docker_services):
    docker_services.start('job-api')
    port = docker_services.wait_for_service("job-api", 9990)
    return f"http://{docker_services.docker_ip}:{port}/api"


@pytest.fixture(scope="session")
def docker():
    return docker_py.from_env()


@pytest.fixture
def jobs_api(docker, docker_services):
    """Setup and teardown the jobs-api for one test."""
    docker_services.start('job-api')
    port = docker_services.wait_for_service("job-api", 9990)

    yield f"http://{docker_services.docker_ip}:{port}/api"

    for container in docker.containers.list():
        if "job-api" in container.name:
            container.kill()
            container.remove()
            print(container.name)
