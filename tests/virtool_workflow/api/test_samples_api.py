import aiohttp
import pytest

from tests.virtool_workflow.api.mocks.mock_sample_routes import TEST_SAMPLE_ID, TEST_SAMPLE
from virtool_workflow.api.samples import SampleProvider
from virtool_workflow.data_model import Sample


@pytest.fixture
def sample_api(http: aiohttp.ClientSession, jobs_api_url: str):
    return SampleProvider(TEST_SAMPLE_ID, http, jobs_api_url)


async def test_get(sample_api):
    sample = await sample_api.get()

    assert isinstance(sample, Sample)
    assert sample.id == sample_api.id

    for key in ["name", "id", "host", "isolate", "locale",
                "paired", "quality", "nuvs", "pathoscope"]:
        assert getattr(sample, key) == TEST_SAMPLE[key]

    for actual, expected in zip(sample.files, TEST_SAMPLE["files"]):
        assert actual == expected
