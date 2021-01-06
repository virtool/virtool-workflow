from pathlib import Path
from virtool_workflow import hooks

import virtool_workflow.abc
import virtool_workflow.storage.utils
from virtool_workflow.uploads.files import FileUpload
from virtool_workflow.execution.run_in_executor import FunctionExecutor
from virtool_workflow_runtime.db.db import Collection
from virtool_workflow.abc import AbstractDatabase


class AnalysisUploader(virtool_workflow.abc.AbstractFileUploader):
    """
    Perform upload by copying files into a specified directory (under the `data_path`).

    File entries are added to the "files" field of the analysis database document.
    """

    def __init__(self, analysis_path: Path, run_in_executor: FunctionExecutor,
                 analyses: AbstractDatabase, analysis_id: str):
        self.analysis_path = analysis_path
        self.run_in_executor = run_in_executor
        self.analyses_db = analyses
        self.analysis_id = analysis_id
        self._marks = []

    def mark(self, upload: FileUpload):
        """Mark a file for upload."""
        self._marks.append(upload)

    async def upload(self):
        """Move marked files to the :obj:`AnalysisUploader.analysis_path` and create database entries."""
        source_paths = [file_upload.path for file_upload in self._marks]
        target_paths = [self.analysis_path/source_path.name for source_path in source_paths]

        await virtool_workflow.storage.utils.move_paths(
            zip(source_paths, target_paths),
            self.run_in_executor
        )

        await self.analyses_db.set_files_on_analysis(zip(self._marks, target_paths), self.analysis_id)


class Analysis(virtool_workflow.WorkflowFixture, param_name="analysis"):

    def __init__(self, _id: str, uploader: virtool_workflow.abc.AbstractFileUploader):
        self._id = _id
        self.uploader = uploader

    async def upload_file(self, file_upload: FileUpload):
        self.uploader.mark(file_upload)

    @staticmethod
    def __fixture__(job_args, run_in_executor, analysis_path: Path, database) -> "Analysis":
        analysis_id = job_args["analysis_id"]
        uploader = AnalysisUploader(analysis_path, run_in_executor, database, analysis_id)

        hooks.before_result_upload(uploader.upload, once=True)

        return Analysis(job_args["analysis_id"], uploader)

