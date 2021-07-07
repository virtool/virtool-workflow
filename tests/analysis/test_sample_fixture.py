from tests.api.mocks.mock_job_routes import TEST_JOB
from tests.api.mocks.mock_sample_routes import TEST_SAMPLE_ID


async def no_op(*args, **kwargs):
    return


async def test_sample_has_read_path(runtime):
    TEST_JOB["args"]["sample_id"] = TEST_SAMPLE_ID
    sample_provider = await runtime.get_or_instantiate("sample_provider")
    sample_provider.download_reads = no_op
    sample = await runtime.get_or_instantiate("sample")

    assert sample.read_paths is not None
    assert sample.reads_path is not None
