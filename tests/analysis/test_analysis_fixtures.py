from pathlib import Path

import virtool_workflow.workflow_fixture
from virtool_workflow.analysis.analysis_jobs import AnalysisArguments
from virtool_workflow.workflow_fixture import WorkflowFixtureScope
from virtool_workflow.analysis.library_types import LibraryTypes


TEST_ANALYSIS_INFO = (
        "1",
        "1",
        "1",
        "1",
        dict(
            _id="1",
            paired=True,
            library_type=LibraryTypes.amplicon,
            quality=dict(
                length=["", "1"],
                count="3"
            )
        ),
        dict(
            subtraction=dict(id="id with spaces")
        )
    )


async def test_analysis_fixture_instantiation():
    with WorkflowFixtureScope() as fixtures:
        fixtures["job_id"] = "1"

        fixtures["analysis_info"] = TEST_ANALYSIS_INFO
        fixtures["data_path"] = Path("virtool")
        fixtures["temp_path"] = Path("temp")

        arguments: AnalysisArguments = await fixtures.instantiate(AnalysisArguments)

        assert fixtures["analysis"] == arguments

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
        assert arguments.library_type == LibraryTypes.amplicon
        assert arguments.raw_path == fixtures["temp_path"]/"raw"

