import pytest

from virtool_workflow.analysis.read_prep import unprepared_reads
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from virtool_workflow.storage.paths import context_directory
from virtool_workflow.analysis.fixtures import paired
from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow.analysis import utils


@pytest.yield_fixture
async def fixtures():
    with WorkflowFixtureScope() as _fixtures:
        _fixtures["job_id"] = "1"
        _fixtures["job_document"] = dict(_id="1")
        _fixtures["job_args"] = dict(
            sample_id="1",
            index_id="1",
            ref_id="1",
            analysis_id="1",
            analysis=dict(
                subtraction=dict(id="id with spaces")
            )
        )

        _fixtures["sample"] = dict(
            _id="1",
            paired=False,
            library_type=LibraryType.other,
            quality=dict(
                length=[0, 100],
                count=3
            ),
            files=[dict(raw=True)],
        )

        _fixtures["number_of_processes"] = 3
        with context_directory("test_virtool") as data_path:
            _fixtures["data_path"] = data_path
            yield _fixtures


async def test_unprepared_reads_fixture(fixtures):

    fixtures["cache_document"] = {}
    fixtures["trimming_parameters"] = None
    fixtures["trimming_output_path"] = None

    await fixtures.instantiate(paired)
    reads = await fixtures.instantiate(unprepared_reads)

    assert reads.paths[0] == fixtures["work_path"]/"reads"/"reads_1.fq.gz"
    assert reads.paths == utils.make_read_paths(fixtures["reads_path"], fixtures["paired"])
    assert reads.min_length == 0
    assert reads.max_length == 100
    assert reads.count == 3

