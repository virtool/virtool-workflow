import gzip
import shutil
from pathlib import Path

from tests.virtool_workflow.api.mocks.mock_sample_routes import TEST_SAMPLE_ID, TEST_SAMPLE
from virtool_workflow import features, Workflow
from virtool_workflow.abc.caches.analysis_caches import ReadsCache
from virtool_workflow.analysis.features.trimming import Trimming
from virtool_workflow.analysis.read_prep.skewer import skewer, trimming_min_length
from virtool_workflow.caching.local import LocalCaches
from virtool_workflow.data_model import Job
from virtool_workflow.runtime.providers import sample_provider


async def test_skewer(http_no_decompress, jobs_api_url, tmpdir, run_subprocess, run_in_executor, analysis_files):
    tmpdir = Path(tmpdir)

    job = Job(
        "test_job",
        {
            "sample_id": TEST_SAMPLE_ID
        },
    )
    sample = await sample_provider(job, http_no_decompress, jobs_api_url).get()

    run_skewer = skewer(
        min_length=trimming_min_length(sample.library_type, sample.max_length),
        quiet=True
    )

    TEST_READ_1 = analysis_files / "paired_small_1.fq.gz"
    TEST_READ_2 = analysis_files / "paired_small_2.fq.gz"
    read_1 = await run_in_executor(shutil.copyfile, TEST_READ_1, tmpdir / TEST_READ_1.name)
    read_2 = await run_in_executor(shutil.copyfile, TEST_READ_2, tmpdir / TEST_READ_2.name)

    reads = (read_1, read_2)

    result = await run_skewer(reads, run_subprocess, run_in_executor)

    assert result.left.name == "reads_1.fq.gz"
    assert result.right.name == "reads_2.fq.gz"

    TEST_CORRECT_1 = analysis_files / "reads_1.fq.gz"
    TEST_CORRECT_2 = analysis_files / "reads_2.fq.gz"

    if not TEST_CORRECT_1.exists() or not TEST_CORRECT_2.exists():
        await run_in_executor(shutil.copyfile, result.left, TEST_CORRECT_1)
        await run_in_executor(shutil.copyfile, result.right, TEST_CORRECT_2)

    with gzip.open(TEST_CORRECT_1) as expected:
        with gzip.open(result.left) as f:
            for line1, line2 in zip(f.readlines(), expected.readlines()):
                assert line1 == line2


async def test_trimming_feature(runtime, tmpdir, http_no_decompress, run_in_executor, data_regression):
    runtime["http"] = http_no_decompress
    TEST_SAMPLE["paired"] = True
    runtime["sample_caches"] = LocalCaches[ReadsCache](Path(tmpdir), run_in_executor)
    job = await runtime.get_or_instantiate("job")
    job.args["sample_id"] = TEST_SAMPLE_ID
    runtime["workflow"] = Workflow()

    trimming_feature = Trimming()

    await features.install_into_environment(runtime, trimming_feature)

    sample = await runtime.get_or_instantiate("sample")

    assert sample.reads_path.exists()
    for path in sample.read_paths:
        assert path.exists()

    assert runtime["fastqc_quality"]
    data_regression.check(runtime["fastqc_quality"])
