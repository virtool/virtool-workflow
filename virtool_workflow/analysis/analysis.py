"""
Fixture and class for representing the analysis associated with a workflow run.

"""
from dataclasses import asdict
from pathlib import Path

from virtool_workflow import data_model, hooks
from virtool_workflow.api.analysis import AnalysisProvider
from virtool_workflow.data_model.files import VirtoolFileFormat

from fixtures import fixture


class Analysis(data_model.Analysis):
    """
    Represents a Virtool analysis.

    Provides access to analysis data and a method :meth:`.upload` that allows selection of files in the workflow
    environment to be uploaded and associated with the analysis on workflow completion.

    """

    def __init__(self, upload_files: callable, *args, **kwargs):
        self.to_upload = []

        @hooks.on_success
        async def _upload_files():
            await upload_files(self.to_upload)
            self.to_upload = []

        super(Analysis, self).__init__(*args, **kwargs)

    def upload(self, path: Path, format: VirtoolFileFormat):
        """
        Mark a file to be uploaded at the end of a workflow run.

        :param path: the path to the file in the workflow work directory
        :param format: the format of the file being uploaded

        """
        self.to_upload.append((path, format))


@fixture
async def analysis(analysis_provider: AnalysisProvider) -> Analysis:
    """
    A fixture that returns an :class:`.Analysis` object representing the analysis associated with the running workflow.

    :param analysis_provider: the analysis provider
    :return: the analysis object

    """
    async def upload_files(files):
        for path, format in files:
            await analysis_provider.upload(path, format)

    _analysis = asdict(await analysis_provider)

    return Analysis(upload_files, **_analysis)
