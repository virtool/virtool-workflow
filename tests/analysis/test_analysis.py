import pytest

from virtool_workflow.analysis.analysis_info import AnalysisInfo, AnalysisArguments
from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow.analysis.read_prep import unprepared_reads
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from virtool_workflow.storage.paths import context_directory


@pytest.yield_fixture
async def fixtures():
    with WorkflowFixtureScope() as _fixtures:
        _fixtures["job_id"] = "1"
        _fixtures["job_document"] = dict(_id="1", args={})
        _fixtures["analysis_info"] = TEST_ANALYSIS_INFO
        _fixtures["number_of_processes"] = 3
        with context_directory("test_virtool") as data_path:
            _fixtures["data_path"] = data_path
            yield _fixtures


TEST_ANALYSIS_INFO = AnalysisInfo(
    sample_id="1",
    index_id="1",
    ref_id="1",
    analysis_id="1",
    sample=dict(
        _id="1",
        paired=False,
        library_type=LibraryType.other,
        quality=dict(
            length=[0, 100],
            count=3
        ),
        files=[dict(raw=True)],
    ),
    analysis=dict(
        subtraction=dict(id="id with spaces")
    )
)


async def test_analysis_fixture_instantiation(fixtures):
    arguments: AnalysisArguments = await fixtures.instantiate(AnalysisArguments)

    assert fixtures["analysis_args"] == arguments

    assert arguments.analysis == TEST_ANALYSIS_INFO.analysis
    assert arguments.sample == TEST_ANALYSIS_INFO.sample
    assert not arguments.paired
    assert arguments.read_count == 3
    assert arguments.sample_read_length == 100
    assert arguments.sample_path == fixtures["data_path"]/"samples/1"
    assert arguments.path == arguments.sample_path/"analysis/1"
    assert arguments.index_path == fixtures["data_path"]/"references/1/1/reference"
    assert arguments.reads_path == fixtures["temp_path"]/"reads"
    assert arguments.subtraction_path == \
           fixtures["data_path"]/"subtractions/id_with_spaces/reference"
    assert arguments.reads_path/"reads_1.fq.gz" in arguments.read_paths
    assert arguments.library_type == LibraryType.other
    assert arguments.raw_path == fixtures["temp_path"]/"raw"


async def test_sub_fixtures_use_same_instance_of_analysis_args(fixtures):

    def use_fixtures(
            analysis_args: AnalysisArguments,
            analysis_path,
            analysis_document,
            sample,
            sample_path
    ):
        assert id(analysis_args.path) == id(analysis_path)
        assert id(analysis_args.analysis) == id(analysis_document)
        assert id(analysis_args.sample) == id(sample)
        assert id(analysis_args.sample_path) == id(sample_path)

    bound = await fixtures.bind(use_fixtures)
    bound()


async def test_unprepared_reads_fixture(fixtures):

    fixtures["cache_document"] = {}
    fixtures["trimming_parameters"] = None
    fixtures["trimming_output_path"] = None

    reads = await fixtures.instantiate(unprepared_reads)

    assert reads.paths[0] == fixtures["temp_path"]/"reads"/"reads_1.fq.gz"
    assert reads.paths == fixtures["analysis_args"].read_paths
    assert reads.min_length == 0
    assert reads.max_length == 100
    assert reads.count == 3

