import filecmp
import sys
from pathlib import Path
from shutil import copy
from typing import Optional, Dict, Any, List

import pytest

from virtool_workflow.abc import AbstractDatabase
import virtool_workflow.analysis.indexes
from virtool_workflow.analysis.indexes import Index

EXPECTED_PATH = Path(sys.path[0]) / "tests/analysis/expected"
FAKE_JSON_PATH = Path(sys.path[0]) / "tests/analysis/reference.json.gz"

OTU_IDS = ["625nhyu8", "n97b7lup", "uasjtbmg", "d399556a"]


class MockDatabase(AbstractDatabase):
    async def fetch_document_by_id(
        self, id_: str, collection_name: str
    ) -> Optional[Dict[str, Any]]:
        if id_ == "foo" and collection_name == "indexes":
            return {"_id": "foo", "reference": {"id": "bar"}}

        if id_ == "bar" and collection_name == "references":
            return {"_id": "bar",
                    "name": "Bar",
                    "data_type": "barcode",
                    "organism": "virus",
                    "targets": []}


@pytest.fixture
def data_path(tmpdir):
    data = tmpdir.mkdir("data")
    return Path(data)


@pytest.fixture
def work_path(tmpdir):
    work = tmpdir.mkdir("work")
    return Path(work)


@pytest.fixture
async def indexes(
    data_path, work_path, run_in_executor, run_subprocess, tmpdir
) -> List[Index]:
    job_args = {"index_id": "foo", "proc": 1}

    index_path = data_path / "references/bar/foo"
    index_path.mkdir(parents=True)

    copy(FAKE_JSON_PATH, index_path / "reference.json.gz")

    database = MockDatabase()

    return await virtool_workflow.analysis.indexes.indexes(
        database,
        job_args,
        data_path,
        work_path,
        run_in_executor,
        run_subprocess,
    )


async def test_indexes(work_path, indexes):
    # Check that single index directory was created
    assert set((work_path / "indexes").iterdir()) == {work_path / "indexes/foo"}

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
    assert indexes[0].compressed_json_path == index_dir_path / "reference.json.gz"
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
            work_path / f"isolates_1.{extension}", f"{EXPECTED_PATH}.{extension}"
        )
