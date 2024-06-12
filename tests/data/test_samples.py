from pathlib import Path

import pytest
from pydantic_factories import ModelFactory
from pyfixtures import FixtureScope
from virtool_core.models.samples import Quality

from virtool_workflow.data.samples import WFNewSample, WFSample
from virtool_workflow.errors import JobsAPIConflictError, JobsAPINotFoundError
from virtool_workflow.pytest_plugin.data import Data

QUALITY = {
    "bases": [
        [30, 31, 31, 31, 31, 31],
        [30, 31, 31, 31, 31, 32],
    ],
    "composition": [
        [32, 14, 4, 40],
        [22, 12, 34, 25],
    ],
    "count": 998822,
    "encoding": "Sanger / Illumina 1.8",
    "gc": 43,
    "length": [0, 52],
    "sequences": [
        0,
        0,
        3512,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ],
}


class TestSample:
    """Tests for the sample fixture that provides sample data for analyses.

    See ``TestNewSample`` for tests of the ``new_sample`` fixture, that is used for
    sample creation workflows.
    """

    @pytest.mark.parametrize("paired", [True, False], ids=["paired", "single"])
    async def test_ok(
        self,
        paired: bool,
        data: Data,
        example_path: Path,
        scope: FixtureScope,
        work_path: Path,
    ):
        """Test that the sample fixture instantiates, contains the expected data, and
        downloads the sample files to the work path.
        """
        data.job.args["sample_id"] = data.sample.id
        data.sample.paired = paired

        sample: WFSample = await scope.instantiate_by_key("sample")

        assert sample.id == data.sample.id
        assert sample.name == data.sample.name
        assert sample.paired == data.sample.paired == paired

        for index, path in enumerate(sample.read_paths):
            file_name = f"reads_{index + 1}.fq.gz"

            assert path == work_path / "reads" / file_name

            with open(path, "rb") as f1, open(
                example_path / "sample" / file_name,
                "rb",
            ) as f2:
                assert f1.read() == f2.read()

            assert path.exists()

    async def test_not_found(self, data: Data, scope: FixtureScope):
        data.job.args["sample_id"] = "not_found"

        with pytest.raises(JobsAPINotFoundError) as err:
            await scope.instantiate_by_key("sample")

        assert "Sample not found" in str(err)


class TestNewSample:
    async def test_ok(
        self,
        data: Data,
        example_path: Path,
        scope: FixtureScope,
        work_path: Path,
    ):
        data.job.args.update(
            {
                "files": [
                    {
                        "id": 1,
                        "name": "reads_1.fq.gz",
                        "size": 100,
                    },
                    {
                        "id": 2,
                        "name": "reads_2.fq.gz",
                        "size": 100,
                    },
                ],
                "sample_id": data.new_sample.id,
            },
        )

        data.job.args["sample_id"] = data.new_sample.id

        new_sample: WFNewSample = await scope.instantiate_by_key("new_sample")

        assert new_sample.id == data.new_sample.id
        assert new_sample.name == data.new_sample.name
        assert new_sample.paired == data.new_sample.paired

        paths = sorted((work_path / "uploads").iterdir())

        assert (
            paths
            == [u.path for u in new_sample.uploads]
            == [
                work_path / "uploads" / "reads_1.fq.gz",
                work_path / "uploads" / "reads_2.fq.gz",
            ]
        )

        for file_name in ("reads_1.fq.gz", "reads_2.fq.gz"):
            with open(work_path / "uploads" / file_name, "rb") as f1, open(
                example_path / "sample" / file_name,
                "rb",
            ) as f2:
                assert f1.read() == f2.read()

    async def test_finalize(self, data: Data, scope: FixtureScope):
        """Test that the finalize method updates the sample with the given quality."""
        data.job.args.update(
            {
                "files": [
                    {
                        "id": 1,
                        "name": "reads_1.fq.gz",
                        "size": 100,
                    },
                    {
                        "id": 2,
                        "name": "reads_2.fq.gz",
                        "size": 100,
                    },
                ],
                "sample_id": data.new_sample.id,
            },
        )

        new_sample = await scope.instantiate_by_key("new_sample")

        assert data.new_sample.ready is False
        assert data.new_sample.quality is None

        await new_sample.finalize(QUALITY)

        assert data.new_sample.ready is True
        assert data.new_sample.quality == Quality(**QUALITY)

    async def test_already_finalized(self, data: Data, scope: FixtureScope):
        """Test that the finalize method raises an error if the sample is already
        finalized.
        """

        class QualityFactory(ModelFactory):
            __model__ = Quality
            __random_seed__ = 1

        data.job.args.update(
            {
                "files": [
                    {
                        "id": 1,
                        "name": "reads_1.fq.gz",
                        "size": 100,
                    },
                    {
                        "id": 2,
                        "name": "reads_2.fq.gz",
                        "size": 100,
                    },
                ],
                "sample_id": data.new_sample.id,
            },
        )

        data.new_sample.ready = True
        data.quality = QualityFactory.build()

        new_sample = await scope.instantiate_by_key("new_sample")

        with pytest.raises(JobsAPIConflictError):
            await new_sample.finalize(QUALITY)

    async def test_delete(self, data: Data, scope: FixtureScope):
        """Test that the delete method deletes the sample."""
        data.job.args.update(
            {
                "files": [
                    {
                        "id": 1,
                        "name": "reads_1.fq.gz",
                        "size": 100,
                    },
                    {
                        "id": 2,
                        "name": "reads_2.fq.gz",
                        "size": 100,
                    },
                ],
                "sample_id": data.new_sample.id,
            },
        )

        new_sample: WFNewSample = await scope.instantiate_by_key("new_sample")

        await new_sample.delete()

        assert data.new_sample is None

    async def test_delete_not_found(self, data: Data, scope: FixtureScope):
        """Test that the delete method raises an error if the sample does not exist."""
        data.job.args.update(
            {
                "files": [
                    {
                        "id": 1,
                        "name": "reads_1.fq.gz",
                        "size": 100,
                    },
                    {
                        "id": 2,
                        "name": "reads_2.fq.gz",
                        "size": 100,
                    },
                ],
                "sample_id": data.new_sample.id,
            },
        )

        new_sample: WFNewSample = await scope.instantiate_by_key("new_sample")

        data.new_sample = None

        with pytest.raises(JobsAPINotFoundError):
            await new_sample.delete()

    async def test_delete_finalized(self, data: Data, scope: FixtureScope):
        """Test that the delete method raises an error if the sample is finalized."""
        data.job.args.update(
            {
                "files": [
                    {
                        "id": 1,
                        "name": "reads_1.fq.gz",
                        "size": 100,
                    },
                    {
                        "id": 2,
                        "name": "reads_2.fq.gz",
                        "size": 100,
                    },
                ],
                "sample_id": data.new_sample.id,
            },
        )

        new_sample: WFNewSample = await scope.instantiate_by_key("new_sample")

        data.new_sample.ready = True

        with pytest.raises(JobsAPIConflictError) as err:
            await new_sample.delete()

        assert "Sample already finalized" in str(err)

    async def test_upload(
        self,
        captured_uploads_path: Path,
        data: Data,
        scope: FixtureScope,
    ):
        """Test that reads can be uploaded to unfinalized samples."""
        data.job.args.update(
            {
                "files": [
                    {
                        "id": 1,
                        "name": "reads_1.fq.gz",
                        "size": 100,
                    },
                    {
                        "id": 2,
                        "name": "reads_2.fq.gz",
                        "size": 100,
                    },
                ],
                "sample_id": data.new_sample.id,
            },
        )

        new_sample: WFNewSample = await scope.instantiate_by_key("new_sample")

        await new_sample.upload(new_sample.uploads[0].path, "fastq")
        await new_sample.upload(new_sample.uploads[1].path, "fastq")

        assert (captured_uploads_path / "reads_1.fq.gz").exists()
        assert (captured_uploads_path / "reads_2.fq.gz").exists()
