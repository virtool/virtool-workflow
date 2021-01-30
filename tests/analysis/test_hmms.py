import sys
from typing import List

import filecmp
from pathlib import Path
from shutil import copy
from virtool_workflow.abc.data_providers.hmms import AbstractHmmsProvider

from virtool_workflow.analysis.hmms import hmms
from virtool_workflow.data_model import HMM

FAKE_PROFILES_PATH = Path(sys.path[0]) / "tests/analysis/profiles.hmm"


def make_mock_hmm(id_, cluster):
    return HMM(id_, cluster, 1, [], {}, {}, False, 1, 0, 0, ("", "", ""))


class TestHmmsProvider(AbstractHmmsProvider):
    @property
    def hmm_list(self) -> List[HMM]:
        return [
            make_mock_hmm("foo", 1),
            make_mock_hmm("bar", 3)
        ]


async def test_hmms(runtime, run_in_executor, run_subprocess, tmpdir):
    runtime.data_providers.hmms_provider = TestHmmsProvider()

    data_path = await runtime.get_or_instantiate("data_path")
    hmms_path = data_path / "hmm"
    hmms_path.mkdir()

    copy(FAKE_PROFILES_PATH, hmms_path)

    hmms_obj = await runtime.instantiate(hmms)

    assert hmms_obj.cluster_annotation_map == {
        1: "foo",
        3: "bar"
    }

    assert filecmp.cmp(hmms_path / "profiles.hmm", hmms_obj.path)

    work_path: Path = runtime["work_path"]

    expected_paths = {
        work_path / "hmms" / f"profiles.hmm{suffix}"
        for suffix in ["", ".h3p", ".h3m", ".h3i", ".h3f"]
    }

    assert set((work_path/"hmms").iterdir()) == expected_paths
