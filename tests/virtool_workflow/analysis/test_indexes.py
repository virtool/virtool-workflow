import filecmp
from pathlib import Path
from typing import Sequence

import aiofiles
import aiohttp
import pytest

from tests.virtool_workflow.api.mocks.mock_index_routes import TEST_INDEX_ID, TEST_REF_ID
from virtool_workflow.analysis.indexes import indexes as indexes_fixture, Index
from virtool_workflow.api.indexes import IndexProvider
from virtool_workflow.execution.run_in_executor import run_in_executor, thread_pool_executor
from virtool_workflow.execution.run_subprocess import run_subprocess
from virtool_workflow.testing import install_as_pytest_fixtures

install_as_pytest_fixtures(globals(), run_in_executor, run_subprocess, thread_pool_executor)


@pytest.fixture
def otu_ids():
    return [
        "pffj4lst",
        "un73lg3c",
    ]


@pytest.fixture
async def indexes_api(http_no_decompress: aiohttp.ClientSession, jobs_api_url: str, work_path: Path):
    return IndexProvider(TEST_INDEX_ID, TEST_REF_ID, http_no_decompress, jobs_api_url)


@pytest.fixture
async def indexes(indexes_api: IndexProvider, work_path, run_in_executor, run_subprocess):
    return await indexes_fixture(indexes_api, work_path, 3, run_in_executor, run_subprocess)


async def test_indexes(indexes: Sequence[Index], work_path):
    index_dir_path = work_path / f"indexes/{TEST_INDEX_ID}"

    # Check that single index directory was created
    assert set((work_path / "indexes").iterdir()
               ) == {work_path / f"indexes/{TEST_INDEX_ID}"}

    assert set(index_dir_path.iterdir()) >= {
        index_dir_path / "otus.json",
        index_dir_path / "otus.json.gz",
    }

    assert len(indexes) == 1

    assert indexes[0].path == index_dir_path
    assert indexes[0].compressed_json_path == index_dir_path / "otus.json.gz"
    assert indexes[0].json_path == index_dir_path / "otus.json"


class TestGetBySequenceID:

    @pytest.mark.parametrize("method_name,result",
                             [("get_sequence_length", 1074), ("get_otu_id_by_sequence_id", "pffj4lst")])
    async def test_success(self, method_name, result, indexes):
        assert getattr(indexes[0], method_name)("7h6yaube") == result

    @pytest.mark.parametrize("method_name,message",
                             [("get_sequence_length", "The sequence_id does not exist in the index"),
                              ("get_otu_id_by_sequence_id", "fart")])
    async def testS_error(self, method_name, message, indexes):
        with pytest.raises(ValueError) as exc:
            getattr(indexes[0], method_name)("foo")
            assert message in str(exc)


async def test_write_isolate_fasta(work_path, indexes, otu_ids, analysis_files, file_regression):
    index = indexes[0]

    path = work_path / "isolates_1.fa"

    await index.write_isolate_fasta(otu_ids, path)

    async with aiofiles.open(path) as f:
        file_regression.check(await f.read())


async def test_build_index(work_path, indexes, otu_ids, analysis_files):
    index = indexes[0]

    path = work_path / "isolates_1"

    await index.build_isolate_index(otu_ids, path, 1)

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
            f"isolates_1.{extension}", f"{analysis_files}/reference.{extension}"
        )
