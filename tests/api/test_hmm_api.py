from pathlib import Path

from pytest import fixture

from tests.api.mocks.mock_hmm_routes import MOCK_HMM
from virtool_workflow.api.hmm import HMMsProvider
from virtool_workflow.data_model import HMM


@fixture
def hmms_api(http, jobs_api_connection_string: str, tmpdir):
    return HMMsProvider(
        http=http,
        jobs_api_connection_string=jobs_api_connection_string,
        work_path=Path(tmpdir),
    )


async def test_get(hmms_api):
    hmm = await hmms_api.get(MOCK_HMM["id"])
    assert isinstance(hmm, HMM)
    assert hmm.id == MOCK_HMM["id"]


async def test_hmm_list(hmms_api):
    hmm_list = await hmms_api.hmm_list()

    assert hmm_list
    for hmm in hmm_list:
        assert isinstance(hmm, HMM)


async def test_get_profiles(hmms_api):
    path = await hmms_api.get_profiles()

    assert path.exists()
