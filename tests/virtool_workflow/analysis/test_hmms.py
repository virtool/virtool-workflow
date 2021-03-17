import filecmp
from pathlib import Path
from shutil import copy
from typing import List

from virtool_workflow.abc.data_providers.hmms import AbstractHMMsProvider
from virtool_workflow.analysis.hmms import hmms
from virtool_workflow.data_model import HMM

FAKE_PROFILES_PATH = Path(__file__).parent / "profiles.hmm"


def make_mock_hmm(id_, cluster):
    return HMM(id_, cluster, 1, [], {}, {}, False, 1, 0, 0, ("", "", ""))


class TestHMMsProvider(AbstractHMMsProvider):
    def __init__(self, path):
        self.path = path

    async def get(self, hmm_id: str):
        pass

    async def get_profiles(self) -> Path:
        pass

    async def hmm_list(self) -> List[HMM]:
        return [
            make_mock_hmm("foo", 1),
            make_mock_hmm("bar", 3)
        ]


async def test_hmms(run_in_executor, run_subprocess, tmpdir):
    data_path = Path(tmpdir) / "data"
    work_path = Path(tmpdir) / "work"
    work_path.mkdir()
    hmms_path = data_path / "hmm"
    hmms_path.mkdir(parents=True)

    copy(FAKE_PROFILES_PATH, hmms_path)

    hmms_obj = await hmms(TestHMMsProvider(hmms_path), tmpdir / "work", data_path, run_in_executor, run_subprocess)

    assert hmms_obj.cluster_annotation_map == {
        1: "foo",
        3: "bar"
    }

    assert filecmp.cmp(hmms_path / "profiles.hmm", hmms_obj.path)

    expected_paths = {
        work_path / "hmms" / f"profiles.hmm{suffix}"
        for suffix in ["", ".h3p", ".h3m", ".h3i", ".h3f"]
    }

    assert set((work_path / "hmms").iterdir()) == expected_paths
