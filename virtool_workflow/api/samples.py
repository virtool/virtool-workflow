from typing import List, Dict, Any

from virtool_workflow.abc.data_providers import AbstractSampleProvider
from virtool_workflow.data_model import Sample
from virtool_workflow.uploads.files import DownloadableFileUpload


class SampleProvider(AbstractSampleProvider):


async def release_files(self):
    pass
