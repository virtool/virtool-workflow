from pathlib import Path

import pytest
from pytest import fixture

from tests.api.mocks.mock_subtraction_routes import (
    TEST_SUBTRACTION_ID,
    TEST_SUBTRACTION,
)
from virtool_workflow.api.errors import AlreadyFinalized
from virtool_workflow.api.subtractions import SubtractionProvider
from virtool_workflow.data_model import WFSubtraction
from virtool_workflow.data_model.files import VirtoolFile


@fixture
def subtraction_api(http, jobs_api_connection_string: str, work_path):
    subtraction_work_path = work_path / "subtractions"
    subtraction_work_path.mkdir(parents=True)

    TEST_SUBTRACTION["ready"] = False

    return SubtractionProvider(
        TEST_SUBTRACTION_ID, http, jobs_api_connection_string, subtraction_work_path
    )


async def test_get(subtraction_api):
    subtraction = await subtraction_api.get()

    assert isinstance(subtraction, WFSubtraction)

    assert subtraction.id == TEST_SUBTRACTION_ID


async def test_upload_file(subtraction_api, work_path):
    test_file = work_path / "subtraction.fa.gz"

    test_file.write_text("ATCG")

    file = await subtraction_api.upload(test_file)

    assert isinstance(file, VirtoolFile)
    assert file.name == test_file.name
    assert file.size == 4


async def test_finalize(subtraction_api):
    updated_subtraction = await subtraction_api.finalize(
        {"a": 0.2, "t": 0.2, "c": 0.2, "g": 0.4}, 100
    )

    assert isinstance(updated_subtraction, WFSubtraction)
    assert updated_subtraction.gc.a == 0.2
    assert updated_subtraction.gc.t == 0.2
    assert updated_subtraction.gc.c == 0.2
    assert updated_subtraction.gc.g == 0.4

    with pytest.raises(AlreadyFinalized):
        await subtraction_api.delete()


async def test_delete(subtraction_api):
    await subtraction_api.delete()
