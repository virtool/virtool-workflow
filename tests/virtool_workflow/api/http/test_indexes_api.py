from pathlib import Path

import aiohttp
import pytest

from tests.virtool_workflow.api.mock_api import TEST_REF_ID, TEST_INDEX_ID
from virtool_workflow.analysis.indexes import Index
from virtool_workflow.api.indexes import IndexProvider
from virtool_workflow.data_model import Reference
from virtool_workflow.data_model.files import VirtoolFile
from virtool_workflow.execution.run_in_executor import run_in_executor, thread_pool_executor
from virtool_workflow.execution.run_subprocess import run_subprocess
from virtool_workflow.testing import install_as_pytest_fixtures

install_as_pytest_fixtures(globals(), run_subprocess, run_in_executor, thread_pool_executor)


@pytest.fixture
async def indexes_api(http: aiohttp.ClientSession, jobs_api_url: str, tmpdir: Path, run_subprocess, run_in_executor):
    return IndexProvider(TEST_INDEX_ID, TEST_REF_ID, tmpdir, http, jobs_api_url, run_in_executor, run_subprocess)


async def test_get(indexes_api):
    index = await indexes_api

    assert isinstance(index, Index)
    assert "c93ec9a9" in index.manifest
    assert index.id == TEST_INDEX_ID
    assert isinstance(index.reference, Reference)
    assert index.reference.id == TEST_REF_ID


async def test_upload(indexes_api: IndexProvider, tmpdir):
    test_file = tmpdir / "reference.fa.gz"
    test_file.write_text("ACTGACG")

    file = await indexes_api.upload(test_file)

    assert isinstance(file, VirtoolFile)
    assert file.name == "reference.fa.gz"
    assert file.format == "fasta"
    assert file.size == 8
