import shutil
from pathlib import Path

from virtool_workflow.analysis.read_prep.fastqc import fastqc
from virtool_workflow.analysis.utils import make_read_paths

TEST_READ_1 = Path(__file__).parent.parent / "paired_small_1.fq.gz"
TEST_READ_2 = Path(__file__).parent.parent / "paired_small_2.fq.gz"


async def test_correct_fastqc(tmpdir, run_subprocess, run_in_executor, data_regression):
    work_path = Path(tmpdir)
    run = fastqc(work_path, run_subprocess)

    await run_in_executor(shutil.copyfile, TEST_READ_1, work_path / "reads_1.fq.gz")
    await run_in_executor(shutil.copyfile, TEST_READ_2, work_path / "reads_2.fq.gz")

    out = await run(make_read_paths(work_path, True))

    data_regression.check(out)
