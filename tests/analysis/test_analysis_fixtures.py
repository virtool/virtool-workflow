import pytest
from pathlib import Path

from virtool_workflow.analysis.analysis_jobs import AnalysisArguments \
    , analysis_path, analysis_document, sample, sample_path
from virtool_workflow.workflow_fixture import WorkflowFixtureScope
from virtool_workflow.analysis.library_types import LibraryType


TEST_ANALYSIS_INFO = (
        "1",
        "1",
        "1",
        "1",
        dict(
            _id="1",
            paired=True,
            library_type=LibraryType.amplicon,
            quality=dict(
                length=["", "1"],
                count="3"
            )
        ),
        dict(
            subtraction=dict(id="id with spaces")
        )
    )


@pytest.yield_fixture
def fixtures():
    with WorkflowFixtureScope() as _fixtures:
        _fixtures["job_id"] = "1"
        _fixtures["analysis_info"] = TEST_ANALYSIS_INFO
        _fixtures["data_path"] = Path("virtool")
        _fixtures["temp_path"] = Path("temp")

        yield _fixtures


async def test_analysis_fixture_instantiation(fixtures):
    arguments: AnalysisArguments = await fixtures.instantiate(AnalysisArguments)

    assert fixtures["analysis_args"] == arguments

    assert arguments.analysis == TEST_ANALYSIS_INFO[5]
    assert arguments.sample == TEST_ANALYSIS_INFO[4]
    assert arguments.paired
    assert arguments.read_count == 3
    assert arguments.sample_read_length == 1
    assert arguments.sample_path == fixtures["data_path"]/"samples/1"
    assert arguments.path == arguments.sample_path/"analysis/1"
    assert arguments.index_path == fixtures["data_path"]/"references/1/1/reference"
    assert arguments.reads_path == fixtures["temp_path"]/"reads"
    assert arguments.subtraction_path == fixtures["data_path"]/"subtractions/id_with_spaces/reference"
    assert arguments.reads_path/"reads_1.fq.gz" in arguments.read_paths
    assert arguments.reads_path/"reads_2.fq.gz" in arguments.read_paths
    assert arguments.library_type == LibraryType.amplicon
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

