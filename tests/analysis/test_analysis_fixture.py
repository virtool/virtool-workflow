from pathlib import Path
from typing import Dict, Any

from virtool_workflow import hooks
from virtool_workflow.abc.data_providers.analysis import AbstractAnalysisProvider
from virtool_workflow.analysis.analysis import FileUpload
from virtool_workflow.data_model import Job


class TestAnalysisProvider(AbstractAnalysisProvider):
    def __init__(self):
        self.uploads = []

    async def store_result(self, result: Dict[str, Any]):
        ...

    async def register_file_upload(self, upload: FileUpload):
        self.uploads.append(upload)

    async def delete(self):
        ...


async def test_upload_file(runtime):
    runtime.data_providers.analysis_provider = analysis_provider = TestAnalysisProvider()

    runtime["job"] = Job(
        _id="test_upload_file",
        args={
            "analysis_id": "1",
            "sample_id": "2"
        },
    )

    test_file = Path("test_file.txt")
    test_file.write_text("test file")

    await runtime.execute_function(lambda analysis, analysis_path:
                                   analysis.upload_file(test_file.name, "A test file", test_file, "fasta"))

    await hooks.before_result_upload.trigger(runtime.scope)

    assert not test_file.exists()
    assert (runtime["analysis_path"] / f"0_{test_file.name}").exists()

    assert test_file.name in [f.name for f in analysis_provider.uploads]
