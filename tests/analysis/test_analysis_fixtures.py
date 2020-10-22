import os
import shutil
import filecmp
from pathlib import Path

import pytest

from . import fastqc_out

from virtool_workflow.analysis.analysis_info import AnalysisArguments, AnalysisInfo
from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow.analysis.read_paths import reads_path
from virtool_workflow.analysis.trim_parameters import trimming_parameters
from virtool_workflow.storage.paths import context_directory
from virtool_workflow.workflow_fixture import WorkflowFixtureScope
from virtool_workflow.analysis.trimming import trimming_output, trimming_output_path, trimming_input_paths
from virtool_workflow.analysis.cache import cache_document
from virtool_workflow.analysis.read_paths import parsed_fastqc

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
                length=["", "100"],
                count="3"
            ),
            files=[dict(raw=True)],
        ),
        analysis=dict(
            subtraction=dict(id="id with spaces")
        )
    )

SAMPLE_FASTQ_DATA = Path(__file__).parent/"large.fq.gz"
SAMPLE_TRIMMED_FASTQ_DATA = Path(__file__).parent/"large_trimmed.fq.gz"


@pytest.yield_fixture
async def fixtures():
    with WorkflowFixtureScope() as _fixtures:
        _fixtures["job_id"] = "1"
        _fixtures["analysis_info"] = TEST_ANALYSIS_INFO
        _fixtures["number_of_processes"] = 3
        with context_directory("test_virtool") as data_path:
            _fixtures["data_path"] = data_path
            sample_path = await _fixtures.get_or_instantiate("sample_path")
            read_location = sample_path / "reads_1.fq.gz"
            if not read_location.exists():
                shutil.copyfile(SAMPLE_FASTQ_DATA, read_location)
            yield _fixtures


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


async def test_correct_trimming_parameters(fixtures):
    params = await fixtures.instantiate(trimming_parameters)
    assert params == {
        "end_quality": "20",
        "mode": "pe",
        "max_error_rate": "0.1",
        "max_indel_rate": "0.03",
        "max_length": None,
        "mean_quality": "25",
        "min_length": 100
    }


async def test_trimming_input_paths(fixtures):
    sample_path = await fixtures.get_or_instantiate("sample_path")

    shutil.copyfile(Path(__file__).parent/"large.fq.gz", sample_path/"reads_1.fq.gz")

    input_paths = await fixtures.instantiate(trimming_input_paths)

    assert input_paths[0].exists()


async def test_correct_trimming_output(fixtures):
    trimmed_read_path, _ = await fixtures.instantiate(trimming_output)

    files = list(trimmed_read_path.glob("*"))
    filenames = [p.name for p in files]

    assert "reads-trimmed.fastq.gz" in filenames
    assert "reads-trimmed.log" in filenames

    output = trimmed_read_path/"reads-trimmed.fastq.gz"
    expected = Path(__file__).parent/"large_trimmed.fq.gz"

    print(os.stat(output))
    print(os.stat(expected))

    assert filecmp.cmp(output, expected)


async def test_parsed_fastqc(fixtures):
    path = await fixtures.instantiate(trimming_output_path)
    fixtures["trimming_output"] = path, "TEST"

    shutil.copyfile(Path(__file__).parent/"large_trimmed.fq.gz", path/"reads-trimmed.fastq.gz")
    (path/"reads-trimmed.log").touch()

    fastqc = await fixtures.instantiate(parsed_fastqc)
    assert fastqc == fastqc_out.expected_output


async def test_instantiate_reads_path_and_caches_used(fixtures):
    trim_path = await fixtures.instantiate(trimming_output_path)
    fixtures["trimming_output"] = trim_path, "TEST"
    fixtures["parsed_fastqc"] = fastqc_out.expected_output

    shutil.copyfile(SAMPLE_TRIMMED_FASTQ_DATA, trim_path/"reads_1.fq.gz")

    path: Path = await fixtures.instantiate(reads_path)

    read_path = path/"reads_1.fq.gz"

    # trimming output correctly moved to reads_path
    assert filecmp.cmp(SAMPLE_TRIMMED_FASTQ_DATA, read_path)

    cache = await fixtures.instantiate(cache_document)
    cache_path = fixtures["cache_path"] / cache["id"] / "reads_1.fq.gz"

    # results have been cached and cache_document created

    assert filecmp.cmp(SAMPLE_TRIMMED_FASTQ_DATA, cache_path)

    del fixtures["reads_path"]
    del fixtures["prepared_reads_and_fastqc"]

    for p in path.glob("*"):
        p.unlink()

    await fixtures.instantiate(reads_path)

    assert filecmp.cmp(SAMPLE_TRIMMED_FASTQ_DATA, read_path)
    assert filecmp.cmp(SAMPLE_TRIMMED_FASTQ_DATA, cache_path)
    # If prepared_reads_and_fastqc fixture was not instantiated then
    # The cache must have been used.
    assert "prepared_reads_and_fastqc" not in fixtures






