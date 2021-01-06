import shutil
from pathlib import Path

import virtool_workflow.abc
import virtool_workflow.storage.utils
import virtool_core.utils
from virtool_workflow.uploads.files import FileUpload
from virtool_workflow.execution.run_in_executor import FunctionExecutor
from virtool_workflow_runtime.db.db import Collection


class AnalysisUploader(virtool_workflow.abc.AbstractFileUploader):
    """
    Perform upload by copying files into a specified directory (under the `data_path`).

    File entries are added to the "files" field of the analysis database document.
    """

    def __init__(self, analysis_path: Path, run_in_executor: FunctionExecutor,
                 analyses: Collection, analysis_id: str):
        self.analysis_path = analysis_path
        self.run_in_executor = run_in_executor
        self.analyses_db = analyses
        self.analysis_id = analysis_id
        self._marks = []

    def mark(self, upload: FileUpload):
        self._marks.append(upload)

    async def upload(self):
        """Move marked files to the :obj:`AnalysisUploader.analysis_path` and create database entries."""
        await virtool_workflow.storage.utils.move_paths(
            ((file_upload.path, self.analysis_path/file_upload.name) for file_upload in self._marks),
            self.run_in_executor
        )

        await self.analyses_db.update_one(dict(_id=self.analysis_id), {
            "$push": {
                "files": {
                    "$each": {
                        [{
                            "name": file_upload.name,
                            "type": file_upload.format,
                            "uploaded_at": virtool_core.utils.timestamp(),
                            "reserved": file_upload.reserved,
                            "ready": True
                        } for file_upload in self._marks]
                    }
                }
            }
        })


class Analysis(virtool_workflow.WorkflowFixture, param_name="analysis"):

    def __init__(self, _id: str, uploader: virtool_workflow.abc.AbstractFileUploader):
        self._id = _id
        self.uploader = uploader

    async def upload_file(self, file_upload: FileUpload):
        self.uploader.mark(file_upload)

    @staticmethod
    def __fixture__(job_args, run_in_executor, analysis_path: Path, database) -> "Analysis":
        uploader = AnalysisUploader(analysis_path, run_in_executor, database, )

        return Analysis(job_args["analysis_id"], uploader)

