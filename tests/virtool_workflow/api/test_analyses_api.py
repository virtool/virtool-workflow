import json
from pathlib import Path

import aiohttp
import pytest

import virtool_workflow.api.errors
from virtool_workflow.api.analysis import get_analysis_by_id, AnalysisProvider
from virtool_workflow.data_model.analysis import Analysis
from virtool_workflow.data_model.files import AnalysisFile


@pytest.fixture
def analysis_api(http: aiohttp.ClientSession, jobs_api_url: str):
    return AnalysisProvider("test_analysis", http, jobs_api_url)


async def test_get_analysis(http: aiohttp.ClientSession, jobs_api_url: str):
    analysis = await get_analysis_by_id("test_analysis", http, jobs_api_url)
    assert isinstance(analysis, Analysis)

    with pytest.raises(virtool_workflow.api.errors.NotFound):
        await get_analysis_by_id("not_an_id", http, jobs_api_url)


async def test_analysis_provider_get(analysis_api):
    analysis = await analysis_api

    assert isinstance(analysis, Analysis)


async def test_analysis_provider_upload(analysis_api):
    test_upload = Path("test.json")

    with test_upload.open("w") as fp:
        json.dump({"foo": "bar"}, fp)

    upload = await analysis_api.upload(test_upload, format="json")

    assert isinstance(upload, AnalysisFile)
    assert upload.name == test_upload.name
    assert upload.format == "json"
    assert upload.size == 14

async def test_analysis_file_download(analysis_api):
    raise False
