from pathlib import Path
from typing import Dict, Any, Iterable, Tuple

from virtool_workflow.abc.data_providers.analysis import AbstractAnalysisProvider
from virtool_workflow.analysis.analysis import FileUpload


class TestAnalysisProvider(AbstractAnalysisProvider):
    def __init__(self):
        self.uploads = []

    async def upload_result(self, result: Dict[str, Any]):
        ...

    async def store_files(self, uploads: Iterable[Tuple[FileUpload, Path]]):
        self.uploads = [upload for upload, path in uploads]

    async def delete(self):
        ...
