from pathlib import Path

import pytest
from pyfixtures import FixtureScope

from virtool_workflow.data.analyses import WFAnalysis
from virtool_workflow.errors import JobsAPIConflict, JobsAPINotFound
from virtool_workflow.pytest_plugin.data import Data


async def test_ok(data: Data, scope: FixtureScope):
    """Test that the analysis fixture returns an Analysis object with the expected values.
    """
    data.job.args["analysis_id"] = data.analysis.id

    analysis = await scope.instantiate_by_key("analysis")

    assert analysis.id == data.analysis.id


async def test_not_found(data: Data, scope: FixtureScope):
    """Test that JobsAPINotFound is raised if the analysis does not exist."""
    data.job.args["analysis_id"] = "not_found"

    with pytest.raises(JobsAPINotFound) as err:
        await scope.instantiate_by_key("analysis")


async def test_upload_file(
    captured_uploads_path: Path, data: Data, scope: FixtureScope, work_path: Path,
):
    """Test that the ``Analysis`` object returned by the fixture can be used to upload an
    analysis file.
    """
    ...

    data.job.args["analysis_id"] = data.analysis.id

    analysis: WFAnalysis = await scope.instantiate_by_key("analysis")

    path = work_path / "blank.txt"

    with open(path, "w") as f:
        f.write("hello world")

    await analysis.upload_file(path, "unknown")

    assert (captured_uploads_path / "blank.txt").read_text() == "hello world"


async def test_delete(data: Data, scope: FixtureScope, work_path: Path):
    """Test that the analysis fixture can be used to delete the analysis it represents."""
    data.job.args["analysis_id"] = data.analysis.id

    analysis: WFAnalysis = await scope.instantiate_by_key("analysis")

    assert data.analysis is not None

    await analysis.delete()

    assert data.analysis is None


async def test_delete_finalized(data: Data, scope: FixtureScope):
    """Test that the analysis fixture raises an error if the analysis is finalized."""
    data.job.args["analysis_id"] = data.analysis.id
    data.analysis.ready = True

    analysis: WFAnalysis = await scope.instantiate_by_key("analysis")

    with pytest.raises(JobsAPIConflict) as err:
        await analysis.delete()

    assert "Analysis is finalized" in str(err)


async def test_result_upload():
    """Test that the analysis fixture can be used to set the analysis result."""
    ...
