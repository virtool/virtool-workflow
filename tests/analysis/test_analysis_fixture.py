from pathlib import Path

from virtool_workflow import hooks
from virtool_workflow.analysis.analysis import Analysis, FileUpload
from virtool_workflow_runtime.config.configuration import db_name, db_connection_string
from virtool_workflow_runtime.db.db import VirtoolDatabase
from virtool_workflow_runtime.test_utils import TestRuntime


async def test_upload_file(runtime: TestRuntime):
    db = VirtoolDatabase(db_name(), db_connection_string())
    await db["analyses"].insert_one(dict(_id="1"))

    runtime.scope["job_args"] = {
        "analysis_id": "1",
        "sample_id": "2"
    }

    test_file = Path("foo")
    test_file.write_text("test file")

    test_file_size = test_file.stat().st_size

    upload = FileUpload(
        "foo",
        "A test file",
        test_file,
        "reads",
    )

    async def use_analysis_fixture(analysis: Analysis, analysis_path: Path):
        await analysis.upload_file(upload)
        await hooks.before_result_upload.trigger(runtime.scope)

        assert not test_file.exists()
        assert (analysis_path/test_file.name).exists()

    await runtime.execute_function(use_analysis_fixture)

    analysis_document = await db["analyses"].find_one(dict(_id="1"))

    file_entry = analysis_document["files"][0]
    assert file_entry["name"] == upload.name
    assert file_entry["description"] == upload.description
    assert file_entry["format"] == upload.format
    assert file_entry["size"] == test_file_size
