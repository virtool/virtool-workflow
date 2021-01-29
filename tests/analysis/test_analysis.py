import pytest

from virtool_workflow.analysis import utils
from virtool_workflow.analysis.fixtures import paired
from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow.analysis.read_prep import unprepared_reads
from virtool_workflow.data_model import Sample


@pytest.fixture
def fixtures(runtime):
    runtime["job"].args = dict(
        sample_id="1",
        index_id="1",
        ref_id="1",
        analysis_id="1",
        analysis=dict(
            subtraction=dict(id="id with spaces")
        )
    )

    runtime["sample"] = Sample(
        id="1",
        name="test_sample",
        isolate="test_isolate",
        host="test_host",
        locale="test_locale",
        paired=False,
        library_type=LibraryType.other,
        quality=dict(
            length=[0, 100],
            count=3
        ),
        files=[],
    )

    return runtime


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

