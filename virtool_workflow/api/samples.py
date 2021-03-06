from pathlib import Path
from typing import Dict, Any

from virtool_workflow.abc.data_providers import AbstractSampleProvider
from virtool_workflow.data_model import Sample
from virtool_workflow.data_model.files import VirtoolFileFormat


class SampleProvider(AbstractSampleProvider):

    async def get(self) -> Sample:
        pass

    async def finalize(self, quality: Dict[str, Any]):
        pass

    async def delete(self):
        pass

    async def upload(self, path: Path, format: VirtoolFileFormat):
        pass

    async def download(self):
        pass


async def release_files(self):
    pass
