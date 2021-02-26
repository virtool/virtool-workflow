import aiohttp
import pytest

import virtool_workflow.api.errors
from virtool_workflow.api.analysis import get_analysis_by_id
from virtool_workflow.data_model.analysis import Analysis


async def test_get_analysis(http: aiohttp.ClientSession, jobs_api_url: str):
    analysis = await get_analysis_by_id("test_analysis", http, jobs_api_url)
    assert isinstance(analysis, Analysis)

    with pytest.raises(virtool_workflow.api.errors.NotFound):
        await get_analysis_by_id("not_an_id", http, jobs_api_url)
       