from datetime import datetime
from pathlib import Path

import pytest
from syrupy.matchers import path_type

from tests.api.mocks.mock_index_routes import (
    TEST_INDEX_ID,
    TEST_INDEX,
    TEST_REF_ID,
)
from virtool_workflow.api.indexes import IndexProvider
from virtool_workflow.data_model.files import VirtoolFile


@pytest.fixture
async def indexes_api(http, jobs_api_connection_string: str):
    return IndexProvider(TEST_INDEX_ID, TEST_REF_ID, http, jobs_api_connection_string)


async def test_get(indexes_api: IndexProvider, snapshot):
    assert await indexes_api.get() == snapshot


async def test_upload(
    indexes_api: IndexProvider,
    tmpdir,
):
    test_file = Path(tmpdir) / "reference.fa.gz"
    test_file.write_text("ACTGACG", encoding="utf-8")

    file = await indexes_api.upload(test_file)

    assert isinstance(file, VirtoolFile)
    assert file.name == "reference.fa.gz"
    assert file.format == "fasta"
    assert file.size == 7


async def test_download(indexes_api: IndexProvider, tmpdir):
    await indexes_api.download(Path(tmpdir))

    print(set(p.name for p in Path(tmpdir).iterdir()))

    assert set(p.name for p in Path(tmpdir).iterdir()) == {
        "otus.json.gz",
        "reference.fa.gz",
        "reference.1.bt2",
        "reference.2.bt2",
        "reference.3.bt2",
        "reference.4.bt2",
        "reference.rev.1.bt2",
        "reference.rev.2.bt2",
    }


async def test_finalize(indexes_api: IndexProvider, snapshot):
    assert await indexes_api.finalize() == snapshot
