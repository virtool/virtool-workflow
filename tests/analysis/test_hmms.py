from pathlib import Path

import pytest
import shutil

from virtool_workflow.analysis.hmms import hmms
from virtool_workflow.api.hmm import HMMsProvider


@pytest.fixture
def profiles_path(analysis_files):
    return analysis_files / "profiles.hmm"


@pytest.mark.skipif(
    shutil.which("hmmpress") is None, reason="hmmpress is not installed."
)
async def test_hmms(
    http, jobs_api_connection_string, run_in_executor, run_subprocess, tmpdir
):
    work_path = Path(tmpdir) / "work"
    work_path.mkdir()

    provider = HMMsProvider(http, jobs_api_connection_string, work_path)

    try:
        await hmms(provider, work_path, run_subprocess)
    except FileNotFoundError as e:
        if "hmmpress" in e.args[0]:
            raise RuntimeError("hmmpress not installed.")
        else:
            raise e
