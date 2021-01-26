"""Test utilities for Virtool Workflows."""
from typing import Dict, Any, List

import pytest

from virtool_workflow.abc.providers.cache import CacheEntry
from virtool_workflow.analysis.runtime import AnalysisWorkflowRuntime
from virtool_workflow.abc.providers import AbstractAnalysisProvider, AbstractCacheProvider
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


class MockCachesProvider(AbstractCacheProvider):

    async def create(self, cache: CacheEntry):
        pass

    async def set_files(self, files: List[dict]):
        pass

    async def set_quality(self, quality: Dict[str, Any]):
        pass

    async def find(self, trimming_parameters: Dict[str, Any], trimming_program: str) -> CacheEntry:
        pass

    async def delete_cache(self):
        pass

    async def clear_caches(self):
        pass

    async def unset_caches_for_analyses(self):
        pass


@pytest.fixture
def runtime():
    return AnalysisWorkflowRuntime(
        Job("1", {}, 2, 2),
        analysis_provider=MockAnalysisProvider(),
        caches_provider=
    )
