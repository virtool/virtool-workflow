from pathlib import Path

from virtool_workflow import hooks
from virtool_workflow.analysis.analysis import Analysis, FileUpload
from virtool_workflow_runtime.config.configuration import db_name, db_connection_string
from virtool_workflow_runtime.db.db import VirtoolDatabase
from virtool_workflow_runtime.test_utils import TestRuntime
from virtool_workflow.db.db import DirectAccessDatabase


async def test_upload_file(runtime: TestRuntime):
    db = VirtoolDatabase(db_name(), db_connection_string())
    await db["analyses"].insert_one(dict(_id="1"))

    runtime.scope["job_args"] = {
        "analysis_id": "1",
        "sample_id": "2"
    }

    runtime.scope["database"] = DirectAccessDatabase(db_name(), db_connection_string())

    test_file = Path("foo")
    test_file.write_text("test file")

    test_file_size = test_file.stat().st_size

    upload = FileUpload(
        "foo",
        "A test file",
        test_file,
        "fasta",
    )

    async def use_analysis_fixture(analysis: Analysis, analysis_path: Path):
        await analysis.upload_file(upload)
        await hooks.before_result_upload.trigger(runtime.scope)

        assert not test_file.exists()
        assert (analysis_path/f"0_{test_file.name}").exists()

    await runtime.execute_function(use_analysis_fixture)

    analysis_document = await db["analyses"].find_one(dict(_id="1"))

    assert analysis_document["files"][0] == {
        "id": f"0_{upload.name}",
        "name": upload.name,
        "description": upload.description,
        "format": upload.format,
        "size": test_file_size,
    }
