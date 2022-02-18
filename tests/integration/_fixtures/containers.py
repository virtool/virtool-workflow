import pytest


@pytest.fixture(scope="module")
def mongo_url(module_scoped_container_getter):
    service = module_scoped_container_getter.get("mongo")
    network_info = service.network_info[0]

    return f"mongodb://{network_info.hostname}:{network_info.host_port}"


@pytest.fixture(scope="module")
def pg_url(module_scoped_container_getter):
    service = module_scoped_container_getter.get("postgres")
    network_info = service.network_info[0]

    return f"postgresql+asyncpg://virtool:virtool@{network_info.hostname}/virtool"


@pytest.fixture(scope="module")
def redis_service(module_scoped_container_getter):
    service = module_scoped_container_getter.get("redis")
    network_info = service.network_info[0]

    return f"redis://{network_info.hostname}:{network_info.host_port}"


@pytest.fixture(scope="module")
def jobs_api_service(module_scoped_container_getter):
    return module_scoped_container_getter.get("jobs-api")


@pytest.fixture
def jobs_api(jobs_api_service):
    network_info = jobs_api_service.network_info[0]

    return f"http://{network_info.hostname}:{network_info.host_port}"

