import pytest
from contextlib import contextmanager

from virtool_workflow.analysis.analysis_info import *
from virtool_workflow.workflow_fixture import WorkflowFixtureScope
from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow.analysis.trim_parameters import trimming_parameters
from virtool_workflow.analysis.read_paths import reads_path
from virtool_workflow.execute import run_shell_command

from virtool_workflow.storage.paths import context_directory


TEST_ANALYSIS_INFO = AnalysisInfo(
        sample_id="1",
        index_id="1",
        ref_id="1",
        analysis_id="1",
        sample=dict(
            _id="1",
            paired=True,
            library_type=LibraryType.amplicon,
            quality=dict(
                length=["", "1"],
                count="3"
            ),
            files=[dict(raw=True)],
        ),
        analysis=dict(
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

    assert arguments.analysis == TEST_ANALYSIS_INFO.analysis
    assert arguments.sample == TEST_ANALYSIS_INFO.sample
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

    bound = await fixtures.bind(use_fixtures)
    bound()


async def test_correct_trimming_parameters(fixtures):
    params = await fixtures.instantiate(trimming_parameters)
    assert params == {
        "end_quality": 0,
        "mode": "pe",
        "max_error_rate": "0.1",
        "max_indel_rate": "0.03",
        "max_length": None,
        "mean_quality": 0,
        "min_length": 1
    }


@contextmanager
def init_reads_dir(path: Path):
    with context_directory(path) as read_dir:
        paths = utils.make_read_paths(read_dir, True)
        for path in paths:
            path.write_text("")

        yield paths


async def test_reads_paths_initialized(fixtures):

    sample_path = await fixtures.get_or_instantiate("sample_path")
    raw_path = await fixtures.get_or_instantiate("raw_path")

    #fixtures["trimming_command"] = ["pwd"]

    with init_reads_dir(sample_path):
        with init_reads_dir(raw_path):

            path = await fixtures.instantiate(reads_path)
            print(path)
            raise
