import filecmp
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from shutil import copy
import sys

from virtool_workflow.analysis.hmms import hmms

FAKE_PROFILES_PATH = Path(sys.path[0]) / "tests/analysis/profiles.hmm"


async def test_hmms(run_in_executor, run_subprocess, tmpdir):
    temp_analysis_path = tmpdir.mkdir("temp")

    data_path = tmpdir.mkdir("data")
    hmms_path = data_path.mkdir("hmm")

    copy(FAKE_PROFILES_PATH, hmms_path)

    cluster_annotation_map = {
        1: "foo",
        3: "bar"
    }

    hmms_obj = await hmms(cluster_annotation_map, data_path, temp_analysis_path, run_in_executor, run_subprocess)

    assert hmms_obj.cluster_annotation_map == cluster_annotation_map

    assert filecmp.cmp(hmms_path / "profiles.hmm", hmms_obj.path)

    expected_paths = {
        temp_analysis_path / "hmms" / f"profiles.hmm{suffix}"
        for suffix in ["", ".h3p", ".h3m", ".h3i", ".h3f"]
    }

    assert set((temp_analysis_path / "hmms").listdir()) == expected_paths
