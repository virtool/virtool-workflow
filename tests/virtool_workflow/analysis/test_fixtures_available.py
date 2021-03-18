import pytest

import virtool_workflow.runtime.fixtures
from tests.virtool_workflow.api.mocks.mock_index_routes import TEST_INDEX_ID, TEST_REF_ID
from tests.virtool_workflow.api.mocks.mock_job_routes import TEST_JOB
from tests.virtool_workflow.api.mocks.mock_sample_routes import TEST_SAMPLE_ID
from tests.virtool_workflow.api.mocks.mock_subtraction_routes import TEST_SUBTRACTION_ID
from virtool_workflow.analysis.analysis import Analysis
from virtool_workflow.analysis.indexes import Index
from virtool_workflow.data_model import Subtraction, Sample, HMM
from virtool_workflow.environment import WorkflowEnvironment


@pytest.fixture
def environment(http, jobs_api_url):
    env = WorkflowEnvironment(virtool_workflow.runtime.fixtures.analysis)

    env["http"] = http
    env["jobs_api_url"] = jobs_api_url

    TEST_JOB["args"]["index_id"] = TEST_INDEX_ID
    TEST_JOB["args"]["ref_id"] = TEST_REF_ID
    TEST_JOB["args"]["subtraction_id"] = TEST_SUBTRACTION_ID
    TEST_JOB["args"]["sample_id"] = TEST_SAMPLE_ID

    return env


def use_all(analysis, indexes, subtractions, sample, hmms):
    assert isinstance(analysis, Analysis)
    assert isinstance(indexes[0], Index)
    assert isinstance(subtractions[0], Subtraction)
    assert isinstance(sample, Sample)
    assert isinstance(hmms[0], HMM)


async def test_fixtures_available(environment):
    await environment.execute_function(use_all)