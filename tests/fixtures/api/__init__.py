from pathlib import Path

import pytest
from aiohttp.test_utils import TestServer, TestClient
from aiohttp.web import Application

from tests.fixtures.api.analyses import create_analyses_routes
from tests.fixtures.api.hmms import create_hmms_routes
from tests.fixtures.api.indexes import create_indexes_routes
from tests.fixtures.api.jobs import create_jobs_routes
from tests.fixtures.api.ml import create_ml_routes
from tests.fixtures.api.samples import create_samples_routes
from tests.fixtures.api.subtractions import create_subtractions_routes
from tests.fixtures.api.uploads import create_uploads_routes
from tests.fixtures.data import Data


@pytest.fixture
async def api_server(
    aiohttp_server, data: Data, example_path: Path, read_file_from_multipart, tmpdir
) -> TestServer:
    app = Application()

    for route in (
        create_analyses_routes(data, example_path, read_file_from_multipart),
        create_hmms_routes(data, example_path),
        create_indexes_routes(data, example_path, read_file_from_multipart),
        create_jobs_routes(data),
        create_ml_routes(data, example_path),
        create_samples_routes(data, example_path, read_file_from_multipart),
        create_subtractions_routes(data, example_path, read_file_from_multipart),
        create_uploads_routes(data, example_path),
    ):
        app.add_routes(route)

    return await aiohttp_server(app)


@pytest.fixture
async def api_client(aiohttp_client, api_server: TestServer) -> TestClient:
    """Create an HTTP client for accessing the mocked Jobs API."""
    return await aiohttp_client(api_server)


@pytest.fixture
async def jobs_api_connection_string(api_server: TestServer) -> str:
    """The connection string for the mock API server."""
    return f"http://{api_server.host}:{api_server.port}"
