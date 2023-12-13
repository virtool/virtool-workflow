import filecmp
from pathlib import Path

import pytest
from pyfixtures import FixtureScope
from virtool_core.models.job import Job

from tests.fixtures.api.utils import SUBTRACTION_FILENAMES
from tests.fixtures.data import Data
from virtool_workflow.data.subtractions import WFSubtraction, WFNewSubtraction
from virtool_workflow.errors import JobsAPIConflict


@pytest.fixture
def _new_subtraction_job(data: Data):
    """A job for creating a new subtraction."""
    data.job.args = {
        "subtraction_id": data.new_subtraction.id,
        "files": [{"id": 3, "name": "subtraction.fa.gz"}],
    }
    data.job.workflow = "create_subtraction"

    return data


class TestSubtractions:
    async def test_ok(self, example_path: Path, data: Data, scope: FixtureScope):
        """
        Test that the subtractions fixture matches the expected data and writes the
        subtraction data files to the work path.
        """
        data.job.args["analysis_id"] = data.analysis.id

        subtractions: list[WFSubtraction] = await scope.instantiate_by_key(
            "subtractions"
        )

        assert len(subtractions) == 1

        subtraction = subtractions[0]

        for subtraction_file in subtraction.files:
            assert filecmp.cmp(
                subtraction.path / subtraction_file.name,
                example_path / "subtraction" / subtraction_file.name,
            )


class TestNewSubtraction:
    async def test_ok(
        self,
        _new_subtraction_job: Job,
        data: Data,
        example_path: Path,
        scope: FixtureScope,
    ):
        """
        Test that the new_subtraction fixture matches the expected data and writes the
        subtraction data files to the work path.
        """

        new_subtraction: WFNewSubtraction = await scope.instantiate_by_key(
            "new_subtraction"
        )

        assert new_subtraction.id == data.new_subtraction.id
        assert new_subtraction.name == data.new_subtraction.name
        assert new_subtraction.nickname == data.new_subtraction.nickname

        assert filecmp.cmp(
            new_subtraction.fasta_path,
            example_path / "subtraction/subtraction.fa.gz",
        )

    async def test_upload_and_finalize(
        self,
        _new_subtraction_job: Job,
        data: Data,
        example_path: Path,
        scope: FixtureScope,
    ):
        new_subtraction: WFNewSubtraction = await scope.instantiate_by_key(
            "new_subtraction"
        )

        for filename in SUBTRACTION_FILENAMES:
            await new_subtraction.upload(example_path / "subtraction" / filename)

        await new_subtraction.finalize({"a": 0.2, "t": 0.2, "c": 0.2, "g": 0.4}, 100)

        assert data.new_subtraction.gc.a == 0.2
        assert data.new_subtraction.gc.t == 0.2
        assert data.new_subtraction.gc.c == 0.2
        assert data.new_subtraction.gc.g == 0.4
        assert data.new_subtraction.count == 100

    async def test_already_finalized(
        self,
        _new_subtraction_job: Job,
        data: Data,
        example_path: Path,
        scope: FixtureScope,
    ):
        """
        Test that an exception is raised when a subtraction is finalized a second time.
        """
        new_subtraction: WFNewSubtraction = await scope.instantiate_by_key(
            "new_subtraction"
        )

        for filename in SUBTRACTION_FILENAMES:
            await new_subtraction.upload(example_path / "subtraction" / filename)

        data.new_subtraction.ready = True

        with pytest.raises(JobsAPIConflict) as err:
            await new_subtraction.finalize(
                {"a": 0.2, "t": 0.2, "c": 0.2, "g": 0.4}, 100
            )

        assert "Subtraction already finalized" in str(err.value)

    async def test_delete(
        self, _new_subtraction_job: Job, data: Data, scope: FixtureScope
    ):
        new_subtraction: WFNewSubtraction = await scope.instantiate_by_key(
            "new_subtraction"
        )

        await new_subtraction.delete()

        assert data.new_subtraction is None
