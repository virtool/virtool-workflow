"""Test utilities for Virtool Workflows."""
from typing import Dict, Any

import pytest

from virtool_workflow.analysis.runtime import AnalysisWorkflowRuntime
from virtool_workflow.abc.providers import AbstractAnalysisProvider
from virtool_workflow.data_model import Job
from virtool_workflow.uploads.files import FileUpload


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


@pytest.fixture
def runtime():
    return AnalysisWorkflowRuntime(
        Job("1", {}, 2, 2),
        analysis_provider=MockAnalysisProvider(),
    )
