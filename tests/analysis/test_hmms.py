import filecmp
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from shutil import copy
import sys

from virtool_workflow.analysis.hmms import hmms
from virtool_workflow.execution.run_in_executor import run_in_executor
from virtool_workflow.execution.run_subprocess import run_subprocess

FAKE_PROFILES_PATH = Path(sys.path[0]) / "tests/analysis/profiles.hmm"


async def test_hmms(tmpdir):
    temp_analysis_path = tmpdir.mkdir("temp")

    data_path = tmpdir.mkdir("data")
    hmms_path = data_path.mkdir("hmm")

    copy(FAKE_PROFILES_PATH, hmms_path)

    run_subprocess_ = run_subprocess()
    run_in_executor_ = run_in_executor(ThreadPoolExecutor())

    cluster_annotation_map = {
        1: "foo",
        3: "bar"
    }

    hmms_obj = await hmms(cluster_annotation_map, data_path, temp_analysis_path, run_in_executor_, run_subprocess_)

    assert hmms_obj.cluster_annotation_map == cluster_annotation_map

    assert filecmp.cmp(hmms_path / "profiles.hmm", hmms_obj.path)

    expected_paths = {
        temp_analysis_path / "hmms" / f"profiles.hmm{suffix}"
        for suffix in ["", ".h3p", ".h3m", ".h3i", ".h3f"]
    }

    assert set((temp_analysis_path / "hmms").listdir()) == expected_paths
