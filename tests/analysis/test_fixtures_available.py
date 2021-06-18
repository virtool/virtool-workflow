import shutil
import pytest

import virtool_workflow.runtime.fixtures
from tests.analysis.test_sample_fixture import no_op
from tests.api.mocks.mock_index_routes import TEST_INDEX_ID, TEST_REF_ID
from tests.api.mocks.mock_job_routes import TEST_JOB
from tests.api.mocks.mock_sample_routes import TEST_SAMPLE_ID
from tests.api.mocks.mock_subtraction_routes import TEST_SUBTRACTION_ID
from virtool_workflow.analysis.analysis import Analysis
from virtool_workflow.analysis.indexes import Index
from virtool_workflow.data_model import Subtraction, Sample, HMM
from virtool_workflow.environment import WorkflowEnvironment


@pytest.fixture
async def environment(http, jobs_api_url):
    env = WorkflowEnvironment(virtool_workflow.runtime.fixtures.analysis)

    env["http"] = http
    env["jobs_api_url"] = jobs_api_url
    env["proc"] = 1

    TEST_JOB["args"]["index_id"] = TEST_INDEX_ID
    TEST_JOB["args"]["ref_id"] = TEST_REF_ID
    TEST_JOB["args"]["subtraction_id"] = TEST_SUBTRACTION_ID
    TEST_JOB["args"]["sample_id"] = TEST_SAMPLE_ID

    sample_provider = await env.get_or_instantiate("sample_provider")

    sample_provider.download_reads = no_op

    return env


def use_analysis(analysis):
    assert isinstance(analysis, Analysis)


def use_index(indexes):
    assert isinstance(indexes[0], Index)


def use_subtractions(subtractions):
    assert isinstance(subtractions[0], Subtraction)


def use_sample(sample):
    assert isinstance(sample, Sample)


def use_hmms(hmms):
    assert isinstance(hmms[0], HMM)


async def test_analysis_available(environment):
    await environment.execute_function(use_analysis)


@pytest.mark.skipif(shutil.which("fastqc") is None,
                    reason="Fastqc is not installed.")
@pytest.mark.skipif(shutil.which("Skewer") is None,
                    reason="Skewer is not installed.")
async def test_sample_available(environment):
    await environment.execute_function(use_sample)


async def test_subtractions_available(environment):
    await environment.execute_function(use_subtractions)


@pytest.mark.skipif(shutil.which("Hmmpress") is None,
                    reason="Hmmpress is not installed.")
async def test_hmms_available(environment):
    await environment.execute_function(use_hmms)


async def test_index_available(environment):
    await environment.execute_function(use_index)
