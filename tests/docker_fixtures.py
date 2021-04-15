import pytest
import docker as docker_py
from pathlib import Path
from types import SimpleNamespace


@pytest.fixture(scope="session")
def docker_compose_files(pytestconfig):
    return [str(Path(__file__).parent / "docker-compose.pytest.yml")]


@pytest.fixture(scope="session")
def redis_service(docker_services, redis_url):
    if redis_url is not None:
        return redis_url

    docker_services.start('redis')
    return f"redis://{docker_services.docker_ip}:{6379}"


@pytest.fixture(scope="session")
def postgres_service(docker_services, postgres_url):
    if postgres_url is not None:
        return postgres_url

    docker_services.start('postgres')
    return ("postresql+asyncpg://virtool:virtool"
            f"@{docker_services.docker_ip}:5432/virtool")


@pytest.fixture(scope="session")
def mongo_service(docker_services, mongo_url):
    if mongo_url is not None:
        return mongo_url

    docker_services.start('postgres')
    return f"redis://{docker_services.docker_ip}:5432"


@pytest.fixture(scope="session")
def connections(mongo_service, postgres_service, redis_service):
    return SimpleNamespace(mongo_url=mongo_service,
                           posgres_url=postgres_service,
                           redis_url=redis_service)


@pytest.fixture(scope="session")
def jobs_api_docker(docker_services):
    docker_services.start('job-api')
    port = docker_services.wait_for_service("job-api", 9990)
    return f"http://{docker_services.docker_ip}:{port}/api"


@pytest.fixture(scope="session")
def docker():
    return docker_py.from_env()


@pytest.fixture
def docker_jobs_api(docker, docker_services):
    """Setup and teardown the jobs-api for one test."""
    docker_services.start('job-api')
    port = docker_services.wait_for_service("job-api", 9990)

    yield f"http://{docker_services.docker_ip}:{port}/api"

    for container in docker.containers.list():
        if "job-api" in container.name:
            container.kill()
            container.remove()
