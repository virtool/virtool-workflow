"""
A data provider for Virtool analysis based on HTTP communication with the Virtool job API.

"""
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, List

import aiofiles
import aiohttp
import dateutil.parser

from virtool_workflow.api.errors import raising_errors_by_status_code
from virtool_workflow.api.utils import upload_file_via_put
from virtool_workflow.data_model.analysis import Analysis
from virtool_workflow.data_model.files import VirtoolFile, VirtoolFileFormat

logger = logging.getLogger(__name__)


def get_analysis_files_from_response_json(json) -> List[VirtoolFile]:
    """
    Generate a list of :class:`.VirtoolFile` objects from a JSON response representing a Virtool analysis.

    :param json: the analysis JSON data
    :return: the list of :class:`.VirtoolFile` objects for the analysis

    """
    try:
        return [
            VirtoolFile(
                id=f["id"],
                name=f["name"],
                name_on_disk=f["name_on_disk"],
                size=f["size"],
                uploaded_at=dateutil.parser.isoparse(f["uploaded_at"]),
                format=f["format"]
            )
            for f in json["files"]
        ]
    except KeyError as error:
        if error.args[0] == "files":
            return []
        raise


async def get_analysis_by_id(analysis_id: str, http: aiohttp.ClientSession, jobs_api_url: str) -> Analysis:
    """
    Get the analysis by id via the jobs API.

    :param analysis_id: The id of the analysis.
    :param http: A :class:`aiohttp.ClientSession` instance.
    :param jobs_api_url: The url for the jobs API server.

    :return: A :class:`virtool_workflow.data_model.analysis.Analysis` instance.

    :raise InsufficientJobRights: When the current job does not have sufficient rights to access the analysis.
    :raise NotFound: When the given :obj:`analysis_id` does not correspond to an existing analysis (HTTP 404).
    :raise KeyError: When the analysis data received from the API is missing a required key.

    """
    async with http.get(f"{jobs_api_url}/analyses/{analysis_id}") as response:
        async with raising_errors_by_status_code(response) as response_json:
            return Analysis(
                id=response_json["id"],
                files=get_analysis_files_from_response_json(response_json),
                ready=response_json["ready"] if "ready" in response_json else False
            )


class AnalysisProvider:
    """
    Use the Virtool Jobs API to perform operations on the current analysis.

    :param analysis_id: The ID of the current analysis as found in the job args.
    :param http: A :class:`aiohttp.ClientSession` instance to be used when making requests.
    :param jobs_api_url: The url to the Jobs API.

    """

    def __init__(self,
                 analysis_id: str,
                 http: aiohttp.ClientSession,
                 jobs_api_url: str):
        self.id = analysis_id
        self.http = http
        self.api_url = jobs_api_url

    async def get(self) -> Analysis:
        """
        Fetch the current analysis.

        """
        return await get_analysis_by_id(self.id, self.http, self.api_url)

    async def upload(self, path: Path, format: VirtoolFileFormat):
        """
        Upload a file in the workflow environment that should be associated with the current analysis.

        :param path: the path to the file to upload
        :param format: the format of the file

        """
        return await upload_file_via_put(
            self.http,
            f"{self.api_url}/analyses/{self.id}/files",
            path,
            format
        )

    async def download(self, file_id: str, target_path: Path) -> Path:
        """
        Download a file associated with the current analysis.

        :param file_id: The ID of the file.
        :param target_path: The path which the file data should be stored under.

        :return: A path to the downloaded file. It will be the `target_path` if one was given.

        :raise NotFound: When either the file or the analysis does not exist (404 status code).

        """
        async with self.http.get(f"{self.api_url}/analyses/{self.id}/files/{file_id}") as response:
            async with raising_errors_by_status_code(response):
                async with aiofiles.open(target_path, "wb") as f:
                    await f.write(await response.read())

        return target_path

    async def upload_result(self, result: Dict[str, Any]) -> Tuple[Analysis, dict]:
        """
        Upload the results dict for the analysis.

        :param result: The results dict.

        :raise InsufficientJobRights: When the current job does not have sufficient rights to modify the analysis.
        :raise NotFound: When there is no analysis with the ID :obj:`.id`.
        :raise AlreadyFinalized: When there is already a result for the analysis.

        """
        async with self.http.patch(f"{self.api_url}/analyses/{self.id}", json={
            "results": result
        }) as response:
            async with raising_errors_by_status_code(response) as analysis_json:
                return Analysis(
                    analysis_json["id"],
                    get_analysis_files_from_response_json(analysis_json)
                ), analysis_json["results"]

    async def delete(self):
        """
        Delete the analysis. This method should be called if the workflow code fails before a result is uploaded.

        :raise InsufficientJobRights: When the current job does not have the appropriate permissions required
            to delete the analysis.
        :raise NotFound: When the analysis has already been deleted.
        :raise AlreadyFinalized: When the analysis has a result uploaded and is viewable in Virtool.
            Jobs are not permitted to delete the analysis after this point.
        """
        async with self.http.delete(f"{self.api_url}/analyses/{self.id}") as response:
            async with raising_errors_by_status_code(response):
                return

    def __await__(self) -> Analysis:
        return self.get().__await__()
