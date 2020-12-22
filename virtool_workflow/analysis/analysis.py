import virtool_workflow.abc
from virtool_workflow.uploads.files import FileUpload
from virtool_workflow.uploads.file_system_upload import DirectoryFileUploader


class Analysis(virtool_workflow.WorkflowFixture, param_name="analysis"):

    def __init__(self, _id: str, uploader: virtool_workflow.abc.AbstractFileUploader):
        self._id = _id
        self.uploader = uploader

    async def upload_file(self, file_upload: FileUpload):
        self.uploader.mark(file_upload)

    @staticmethod
    def __fixture__(job_args, upload_path, run_in_executor) -> "Analysis":
        return Analysis(job_args["analysis_id"], DirectoryFileUploader(upload_path, run_in_executor))

