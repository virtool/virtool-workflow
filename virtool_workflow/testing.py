"""Test utilities for Virtool Workflows."""
import pytest
from typing import Dict, Any

from virtool_workflow.abc.providers import AbstractAnalysisProvider
from virtool_workflow.analysis.runtime import AnalysisWorkflowRuntime
from virtool_workflow.data_model import Job
from virtool_workflow.uploads.files import FileUpload
from virtool_workflow.storage.paths import context_directory


class MockAnalysisProvider(AbstractAnalysisProvider):

    def __init__(self):
        self.result = None
        self.uploads = []

    async def store_result(self, result: Dict[str, Any]):
        self.result = result

    async def register_file_upload(self, upload: FileUpload):
        self.uploads.append(upload)

    async def delete(self):
        del self.result
        del self.uploads


def testing_data_path():
    with context_directory("virtool") as data_path:
        yield data_path


@pytest.fixture
def runtime():
    with AnalysisWorkflowRuntime(
        Job("test_job", {}),
        analysis_provider=MockAnalysisProvider()
    ) as _runtime:
        _runtime.override("data_path", testing_data_path)
        yield _runtime


__all__ = [
    "runtime",
    "MockAnalysisProvider"
]
