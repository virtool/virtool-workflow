import filecmp
import sys
from pathlib import Path
from shutil import copy
from typing import Any, Dict, List, Optional

import pytest
import virtool_workflow.analysis.indexes
from virtool_workflow.abc import AbstractDatabase
from virtool_workflow.abc.data_providers.indexes import AbstractIndexProvider
from virtool_workflow.analysis.indexes import Index
from virtool_workflow.data_model import Reference
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow_runtime.config.configuration import \
    work_path as work_path_fixture

EXPECTED_PATH = Path(sys.path[0]) / "tests/analysis/expected"
FAKE_JSON_PATH = Path(sys.path[0]) / "tests/analysis/reference.json.gz"

OTU_IDS = ["625nhyu8", "n97b7lup", "uasjtbmg", "d399556a"]


class TestIndexProvider(AbstractIndexProvider):

    def __init__(self):
        self.has_json = False

    async def fetch_reference(self):
        return Reference("bar", "barcode", "", "Bar", "")

    async def set_has_json(self):
        self.has_json = True


@pytest.fixture
async def work_path():
    with FixtureScope() as scope:
        yield await scope.instantiate(work_path_fixture)


@pytest.fixture
async def indexes_and_runtime(runtime):
    runtime.data_providers.index_provider = TestIndexProvider()
    runtime["job_args"] = {"index_id": "foo", "ref_id": "bar", "proc": 1}

    index_path = await runtime.get_or_instantiate("index_path")

    copy(FAKE_JSON_PATH, index_path / "reference.json.gz")

    indexes = await runtime.instantiate(virtool_workflow.analysis.indexes.indexes)

    return indexes, runtime


@pytest.fixture
def indexes(indexes_and_runtime):
    indexes, _ = indexes_and_runtime
    return indexes


async def test_indexes(indexes_and_runtime):
    indexes, runtime = indexes_and_runtime
    work_path = runtime["work_path"]

    # Check that single index directory was created
    assert set((work_path / "indexes").iterdir()
               ) == {work_path / "indexes/foo"}

    # Check that single reference directory was created
    assert set((work_path / "indexes/foo").iterdir()) == {
        work_path / "indexes/foo/reference.json",
        work_path / "indexes/foo/reference.json",
        work_path / "indexes/foo/reference.json",
        work_path / "indexes/foo/reference.json.gz",
    }

    assert len(indexes) == 1

    index_dir_path = work_path / "indexes/foo"

    assert indexes[0].path == index_dir_path
    assert indexes[0].compressed_json_path == index_dir_path / \
        "reference.json.gz"
    assert indexes[0].json_path == index_dir_path / "reference.json"


class TestGetBySequenceID:

    @pytest.mark.parametrize("method_name,result", [("get_sequence_length", 6508), ("get_otu_id_by_sequence_id", "dpgsl7b4")])
    async def test_success(self, method_name, result, indexes):
        assert getattr(indexes[0], method_name)("b5j2i1mz") == result

    @pytest.mark.parametrize("method_name,message", [("get_sequence_length", "The sequence_id does not exist in the index"), ("get_otu_id_by_sequence_id", "fart")])
    async def testS_error(self, method_name, message, indexes):
        with pytest.raises(ValueError) as exc:
            getattr(indexes[0], method_name)("foo")
            assert message in str(exc)


async def test_write_isolate_fasta(work_path, indexes):
    index = indexes[0]

    path = work_path / "isolates_1.fa"

    await index.write_isolate_fasta(OTU_IDS, path)

    assert filecmp.cmp(path, f"{EXPECTED_PATH}.fa")


async def test_build_index(work_path, indexes):
    index = indexes[0]

    path = work_path / "isolates_1"

    await index.build_isolate_index(OTU_IDS, path, 1)

    for extension in [
        "1.bt2",
        "2.bt2",
        "3.bt2",
        "4.bt2",
        "rev.1.bt2",
        "rev.2.bt2",
        "fa",
    ]:
        assert filecmp.cmp(
            work_path /
            f"isolates_1.{extension}", f"{EXPECTED_PATH}.{extension}"
        )
