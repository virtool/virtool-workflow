from virtool_workflow.data_model import Job
from typing import Iterable, Tuple
from pathlib import Path

from virtool_workflow.uploads.files import FileUpload


def convert_job_to_job_document(job: Job):
    return {
        "_id": job._id,
        "args": job.args,
        "mem": job.mem,
        "proc": job.proc,
        "task": job.task,
        "status": job.status,
    }


def convert_file_uploads_to_documents(files: Iterable[Tuple[FileUpload, Path]]):
    return [{
        "id": destination_path.name,
        "name": file_upload.path.name,
        "description": file_upload.description,
        "format": file_upload.format,
        "size": destination_path.stat().st_size
    } for file_upload, destination_path in files]
