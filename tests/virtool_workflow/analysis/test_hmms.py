from pathlib import Path

import pytest

from virtool_workflow.analysis.hmms import hmms
from virtool_workflow.api.hmm import HMMsProvider


@pytest.fixture
def profiles_path(analysis_files):
    return analysis_files / "profiles.hmm"


async def test_hmms(http, jobs_api_url, run_in_executor, run_subprocess, tmpdir):
    work_path = Path(tmpdir) / "work"
    work_path.mkdir()

    provider = HMMsProvider(http, jobs_api_url, work_path)

    await hmms(provider, work_path, run_subprocess)
