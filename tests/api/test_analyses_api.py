import json
from pathlib import Path

import pytest
from virtool_core.models.analysis import Analysis

import virtool_workflow.api.errors
from virtool_workflow import api
from virtool_workflow.api.analysis import AnalysisProvider
from virtool_workflow.data_model.files import VirtoolFile


@pytest.fixture
def analysis_api(http, jobs_api_connection_string: str):
    return AnalysisProvider("test_analysis", http, jobs_api_connection_string)


async def test_analysis_provider_get(analysis_api):
    analysis = await analysis_api.get()
    assert isinstance(analysis, Analysis)


async def test_analysis_provider_get_not_found(analysis_api):
    analysis_api.id = "not_an_id"

    with pytest.raises(virtool_workflow.api.errors.NotFound):
        await analysis_api.get()


async def test_analysis_provider_upload(analysis_api):
    test_upload = Path("test.txt")

    with test_upload.open("w") as fp:
        json.dump({"foo": "bar"}, fp)

    upload = await analysis_api.upload(test_upload, fmt="json")

    assert isinstance(upload, VirtoolFile)
    assert upload.name == test_upload.name
    assert upload.format == "json"
    assert upload.size == 14

    test_upload.unlink()


async def test_analysis_file_download(analysis_api):
    file_path = await analysis_api.download("0", Path("download.txt"))

    assert file_path.read_text() == "TEST\n"

    file_path.unlink()


async def test_analysis_delete(analysis_api):
    await analysis_api.delete()

    analysis_api.id = "foobar"

    with pytest.raises(api.errors.NotFound):
        await analysis_api.delete()


async def test_result_upload(analysis_api):
    mock_result = {"foo": "bar"}
    analysis, result = await analysis_api.upload_result(mock_result)

    assert isinstance(analysis, Analysis)
    assert result == mock_result
