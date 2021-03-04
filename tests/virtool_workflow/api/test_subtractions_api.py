from pathlib import Path

import aiohttp
from pytest import fixture

from tests.virtool_workflow.api.mocks.mock_subtraction_routes import TEST_SUBTRACTION_ID
from virtool_workflow.api.subtractions import SubtractionProvider
from virtool_workflow.data_model import Subtraction
from virtool_workflow.data_model.files import VirtoolFile


@fixture
def work_path(tmpdir):
    return Path(tmpdir)


@fixture
def subtraction_api(http: aiohttp.ClientSession, jobs_api_url: str, work_path):
    subtraction_work_path = work_path / "subtractions"
    subtraction_work_path.mkdir(parents=True)

    return SubtractionProvider(
        TEST_SUBTRACTION_ID,
        http,
        jobs_api_url,
        subtraction_work_path
    )


async def test_get(subtraction_api):
    subtraction = await subtraction_api.get()

    assert isinstance(subtraction, Subtraction)

    assert subtraction.id == TEST_SUBTRACTION_ID


async def test_upload_file(subtraction_api, work_path):
    test_file = work_path / "subtraction.fa.gz"

    test_file.write_text("ATCG")

    file = await subtraction_api.upload(test_file)

    assert isinstance(file, VirtoolFile)
    assert file.name == test_file.name
    assert file.size == 4
