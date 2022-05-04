import gzip
import shutil
from pathlib import Path

import pytest

from tests.api.mocks.mock_sample_routes import TEST_SAMPLE_ID
from virtool_workflow.analysis.skewer import calculate_trimming_min_length, skewer
from virtool_workflow.data_model import Job
from virtool_workflow.runtime.providers import sample_provider


@pytest.mark.slow
@pytest.mark.skipif(shutil.which("skewer") is None, reason="Skewer is not installed.")
async def test_skewer(
    http,
    jobs_api_connection_string,
    tmpdir,
    run_subprocess,
    run_in_executor,
    analysis_files,
    file_regression,
):
    tmpdir = Path(tmpdir)

    job = Job(
        "test_job",
        {"sample_id": TEST_SAMPLE_ID},
    )
    sample = await sample_provider(job, http, jobs_api_connection_string).get()

    run_skewer = skewer(
        min_length=calculate_trimming_min_length(
            sample.library_type, sample.max_length
        ),
        quiet=True,
    )

    TEST_READ_1 = analysis_files / "paired_small_1.fq.gz"
    TEST_READ_2 = analysis_files / "paired_small_2.fq.gz"
    read_1 = await run_in_executor(
        shutil.copyfile, TEST_READ_1, tmpdir / TEST_READ_1.name
    )
    read_2 = await run_in_executor(
        shutil.copyfile, TEST_READ_2, tmpdir / TEST_READ_2.name
    )

    reads = (read_1, read_2)

    result = await run_skewer(reads, run_subprocess, run_in_executor)

    assert result.left.name == "reads_1.fq.gz"
    assert result.right.name == "reads_2.fq.gz"

    with gzip.open(result.right) as right:
        with gzip.open(result.left) as left:
            file_regression.check(right.read(), basename="right", binary=True)
            file_regression.check(left.read(), basename="left", binary=True)
