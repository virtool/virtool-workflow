import gzip
import shutil
from base64 import b64encode
from pathlib import Path

import arrow
import pytest

from tests.api.mocks.mock_sample_routes import TEST_SAMPLE_ID
from virtool_workflow.analysis.skewer import calculate_trimming_min_length, skewer
from virtool_workflow.data_model.jobs import WFJob
from virtool_workflow.runtime.providers import sample_provider


@pytest.mark.slow
@pytest.mark.skipif(shutil.which("skewer") is None, reason="Skewer is not installed.")
async def test_skewer(
    http,
    jobs_api_connection_string: str,
    tmpdir,
    run_subprocess,
    analysis_files,
    file_regression,
):
    tmpdir = Path(tmpdir)

    job = WFJob(
        **{
            "id": "zzpugkyt",
            "archived": False,
            "args": {"sample_id": TEST_SAMPLE_ID},
            "created_at": arrow.utcnow().isoformat(),
            "key": b64encode(b"test_key").decode("utf-8"),
            "user": {"id": "abc12345", "handle": "igboyes", "administrator": True},
            "rights": {},
            "progress": 60,
            "state": "running",
            "status": [
                {
                    "state": "waiting",
                    "stage": None,
                    "error": None,
                    "progress": 0,
                    "timestamp": "2018-02-06T22:15:52.664000Z",
                },
            ],
            "workflow": "nuvs",
        }
    )

    sample = await sample_provider(job, http, jobs_api_connection_string).get()

    run_skewer = skewer(
        min_length=calculate_trimming_min_length(
            sample.library_type, sample.max_length
        ),
        quiet=True,
    )

    test_read_1 = analysis_files / "paired_small_1.fq.gz"
    test_read_2 = analysis_files / "paired_small_2.fq.gz"

    reads = (
        shutil.copyfile(test_read_1, tmpdir / test_read_1.name),
        shutil.copyfile(test_read_2, tmpdir / test_read_2.name),
    )

    result = await run_skewer(reads, run_subprocess)

    assert result.left.name == "reads_1.fq.gz"
    assert result.right.name == "reads_2.fq.gz"

    with gzip.open(result.right) as right:
        with gzip.open(result.left) as left:
            file_regression.check(right.read(), basename="right", binary=True)
            file_regression.check(left.read(), basename="left", binary=True)
