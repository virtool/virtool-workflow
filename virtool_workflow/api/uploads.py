import asyncio
from pathlib import Path
from typing import Dict, List, Protocol

from fixtures import fixture
from virtool_workflow.api.utils import read_file_from_response
from virtool_workflow.data_model.jobs import Job


class FileDownloader(Protocol):
    async def __call__(self, file_id: str, target: Path) -> Path:
        """
        Download a file.

        :param file_id: The unique ID fo the file.
        :type file_id: str
        :param target: The path to which the file is downloaded.
        :type target: Path

        :returns: The target path, now locating the downloaded file.
        :rtype: Path
        """


@fixture(protocol=FileDownloader)
def download_input_file(http, jobs_api_url: str) -> FileDownloader:
    """Download files from Virtool's uploads API."""
    async def download(file_id, target):
        target_url = f"{jobs_api_url}/uploads/{file_id}"
        async with http.get(target_url) as response:
            return await read_file_from_response(response, target)

    return download


@fixture
def files_list(job: Job) -> List[dict]:
    """The files dictionary for the current job."""
    return job.args["files"]


@fixture
async def input_files(
    files_list: List[dict],
    download_input_file: FileDownloader,
    work_path: Path
) -> Dict[str, Path]:
    """
    The downloaded input files for the current workflow run.

    :returns: A dictionary mapping file names to their locations on disk.
    """
    target_dir = work_path/"files"
    target_dir.mkdir()

    downloads = await asyncio.gather(
        *[
            download_input_file(f["id"], target_dir/f["name"])
            for f in files_list
        ],
        return_exceptions=True
    )

    for f in downloads:
        if isinstance(f, Exception):
            raise f

    return {f["name"]: path for f, path in zip(files_list, downloads)}
