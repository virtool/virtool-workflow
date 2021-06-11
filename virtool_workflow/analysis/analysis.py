"""
Fixture and class for representing the analysis associated with a workflow run.

"""
from dataclasses import asdict
from pathlib import Path

from virtool_workflow import data_model
from virtool_workflow import fixture
from virtool_workflow import hooks
from virtool_workflow.abc.data_providers.analysis import AbstractAnalysisProvider
from virtool_workflow.data_model.files import VirtoolFileFormat


class Analysis(data_model.Analysis):
    """Operations relating to the current analysis, including file uploads."""

    def __init__(self, upload_files: callable, *args, **kwargs):
        self.to_upload = []

        @hooks.on_success
        async def _upload_files():
            await upload_files(self.to_upload)
            self.to_upload = []

        super(Analysis, self).__init__(*args, **kwargs)

    def upload(self, path: Path, format: VirtoolFileFormat):
        """Mark a file to be uploaded at the end of a workflow run."""
        self.to_upload.append((path, format))


@fixture
async def analysis(analysis_provider: AbstractAnalysisProvider) -> Analysis:
    """
    Returns an :class:`.Analysis` object representing the analysis associated with the running workflow.

    :param analysis_provider: the analysis provider
    :return: the analysis object

    """
    async def upload_files(files):
        for path, format in files:
            await analysis_provider.upload(path, format)

    _analysis = asdict(await analysis_provider)

    return Analysis(upload_files, **_analysis)
