from pathlib import Path

import aiofiles
import arrow
import pytest
from aiohttp import MultipartReader

from virtool_workflow.runtime.config import RunConfig


@pytest.fixture
def captured_uploads_path(tmpdir) -> Path:
    """File uploads to the testing API will be written here. Use this path to make
    assertions about the contents of uploaded files.
    """
    path = Path(tmpdir) / "captured_uploads"
    path.mkdir(exist_ok=True, parents=True)

    return path


@pytest.fixture
def example_path(virtool_workflow_example_path: Path) -> Path:
    """The path to example data files for virtool-workflow."""
    return virtool_workflow_example_path


@pytest.fixture
def read_file_from_multipart(captured_uploads_path: Path):
    """Reads the file from a ``MultiPartReader`` and writes it to ``captured_uploads_path.

    Use this in testing API endpoints that accept file uploads.
    """

    async def func(name: str, multipart: MultipartReader):
        file = await multipart.next()

        size = 0

        async with aiofiles.open(captured_uploads_path / name, "wb") as f:
            while True:
                chunk = await file.read_chunk(1024 * 1024 * 10)

                if not chunk:
                    break

                await f.write(chunk)
                size += len(chunk)

        return {
            "id": 1,
            "description": None,
            "name": name,
            "format": "unknown",
            "name_on_disk": f"1-{name}",
            "size": size,
            "uploaded_at": arrow.utcnow().naive,
        }

    return func


@pytest.fixture
def redis_url(pytestconfig):
    return pytestconfig.getoption("redis_url")


@pytest.fixture
def run_config(jobs_api_connection_string: str, work_path: Path) -> RunConfig:
    return RunConfig(
        dev=False,
        jobs_api_connection_string=jobs_api_connection_string,
        mem=8,
        proc=2,
        work_path=work_path,
    )


@pytest.fixture
def work_path(tmpdir) -> Path:
    """A temporary ``work_path`` for testing workflows."""
    path = Path(tmpdir) / "work"
    path.mkdir()

    return path
