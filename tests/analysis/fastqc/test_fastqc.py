import shutil
from pathlib import Path

import pytest

from virtool_workflow.analysis.fastqc import fastqc
from virtool_workflow.analysis.utils import make_read_paths


@pytest.mark.slow
@pytest.mark.skipif(shutil.which("fastqc") is None, reason="Fastqc is not installed.")
async def test_correct_fastqc(tmpdir, run_subprocess, data_regression, analysis_files):
    work_path = Path(tmpdir)
    run = fastqc(work_path, run_subprocess)

    shutil.copyfile(
        analysis_files / "paired_small_1.fq.gz",
        work_path / "reads_1.fq.gz",
    )

    shutil.copyfile(
        analysis_files / "paired_small_2.fq.gz",
        work_path / "reads_2.fq.gz",
    )

    out = await run(make_read_paths(work_path, True))

    data_regression.check(out)
