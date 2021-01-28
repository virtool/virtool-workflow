from pathlib import Path

import virtool_workflow.abc
import virtool_workflow.storage.utils
from virtool_workflow import fixture
from virtool_workflow import hooks
from virtool_workflow.abc.data_providers.analysis import AbstractAnalysisProvider
from virtool_workflow.execution.run_in_executor import FunctionExecutor
from virtool_workflow.uploads.files import FileUpload, VirtoolFileFormat


class AnalysisUploader(virtool_workflow.abc.AbstractFileUploader):
    """
    Perform upload by copying files into a specified directory (under the `data_path`).

    File entries are added to the "files" field of the analysis database document.
    """

    def __init__(self, analysis_path: Path, run_in_executor: FunctionExecutor,
                 analysis_provider: AbstractAnalysisProvider, analysis_id: str):
        self.analysis_path = analysis_path
        self.run_in_executor = run_in_executor
        self.provider = analysis_provider
        self.analysis_id = analysis_id
        self._marks = []

    def mark(self, upload: FileUpload):
        """Mark a file for upload."""
        self._marks.append(upload)

    async def upload(self):
        """Move marked files to the :obj:`AnalysisUploader.analysis_path` and create database entries."""
        source_paths = [file_upload.path for file_upload in self._marks]
        target_paths = [
            self.analysis_path/f"{n}_{source_path.name}" for n, source_path in enumerate(source_paths)]

        await virtool_workflow.storage.utils.move_paths(
            zip(source_paths, target_paths),
            self.run_in_executor
        )

        for mark in self._marks:
            await self.provider.register_file_upload(mark)


class Analysis:
    """Operations relating to the current analysis, including file uploads."""

    def __init__(self, _id: str, uploader: virtool_workflow.abc.AbstractFileUploader):
        self._id = _id
        self.uploader = uploader

    def upload_file(self, name: str, description: str, path: Path, format: VirtoolFileFormat):
        """Mark a file to be uploaded at the end of a workflow run."""
        self.uploader.mark(FileUpload(name, description, path, format))


@fixture
def analysis(job, run_in_executor, analysis_path: Path, analysis_provider: AbstractAnalysisProvider) -> Analysis:
    analysis_id = job.args["analysis_id"]
    uploader = AnalysisUploader(
        analysis_path, run_in_executor, analysis_provider, analysis_id)

    hooks.before_result_upload(uploader.upload, once=True)

    return Analysis(job.args["analysis_id"], uploader)
