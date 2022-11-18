"""
A data provider for Virtool analysis based on HTTP communication with the Virtool API.

"""
from logging import getLogger
from pathlib import Path
from typing import Dict, Any, Tuple

import aiofiles
import aiohttp
from virtool_core.models.analysis import Analysis

from virtool_workflow.api.errors import raising_errors_by_status_code
from virtool_workflow.api.utils import upload_file_via_put, retry
from virtool_workflow.data_model.files import VirtoolFileFormat

logger = getLogger("api")


class AnalysisProvider:
    """
    Use the Virtool Jobs API to perform operations on the current analysis.

    :param analysis_id: The ID of the current analysis as found in the job args.
    :param http: A :class:`aiohttp.ClientSession` instance to be used when making requests.
    :param api_connection_string: The url to the Jobs API.

    """

    def __init__(
        self,
        analysis_id: str,
        http: aiohttp.ClientSession,
        api_connection_string: str,
    ):
        self.id = analysis_id
        self.http = http
        self.api_connection_string = api_connection_string

    async def get(self) -> Analysis:
        """
        Fetch the current analysis.

        :return: a :class:`virtool_workflow.analysis.analysis.Analysis` instance.

        :raise InsufficientJobRights: When the current job does not have sufficient rights to access the analysis.
        :raise NotFound: When the given :obj:`analysis_id` does not correspond to an existing analysis (HTTP 404).
        :raise KeyError: When the analysis data received from the API is missing a required key.

        """
        async with self.http.get(
            f"{self.api_connection_string}/analyses/{self.id}"
        ) as response:
            async with raising_errors_by_status_code(response) as response_json:
                return Analysis(**response_json)

    async def upload(self, path: Path, fmt: VirtoolFileFormat):
        """
        Upload a file in the workflow environment that should be associated with the
        current analysis.

        :param path: the path to the file to upload
        :param fmt: the format of the file

        """
        return await upload_file_via_put(
            self.http,
            f"{self.api_connection_string}/analyses/{self.id}/files",
            path,
            fmt,
        )

    async def download(self, file_id: str, target_path: Path) -> Path:
        """
        Download a file associated with the current analysis.

        :param file_id: The ID of the file.
        :param target_path: The path which the file data should be stored under.

        :return: A path to the downloaded file. It will be the `target_path` if one was given.

        :raise NotFound: When either the file or the analysis does not exist (404 status code).

        """
        async with self.http.get(
            f"{self.api_connection_string}/analyses/{self.id}/files/{file_id}"
        ) as response:
            async with raising_errors_by_status_code(response):
                async with aiofiles.open(target_path, "wb") as f:
                    await f.write(await response.read())

        return target_path

    @retry
    async def upload_result(self, result: Dict[str, Any]) -> Tuple[Analysis, dict]:
        """
        Upload the results dict for the analysis.

        :param result: The results dict.

        :raise InsufficientJobRights: When the current job does not have sufficient rights to modify the analysis.
        :raise NotFound: When there is no analysis with the ID :obj:`.id`.
        :raise AlreadyFinalized: When there is already a result for the analysis.

        """
        async with self.http.patch(
            f"{self.api_connection_string}/analyses/{self.id}", json={"results": result}
        ) as response:
            async with raising_errors_by_status_code(response) as response_json:
                return (
                    Analysis(**response_json),
                    response_json["results"],
                )

    async def delete(self):
        """
        Delete the analysis. This method should be called if the workflow code fails before a result is uploaded.

        :raise InsufficientJobRights: When the current job does not have the appropriate permissions required
            to delete the analysis.
        :raise NotFound: When the analysis has already been deleted.
        :raise AlreadyFinalized: When the analysis has a result uploaded and is viewable in Virtool.
            Jobs are not permitted to delete the analysis after this point.
        """
        async with self.http.delete(
            f"{self.api_connection_string}/analyses/{self.id}"
        ) as response:
            async with raising_errors_by_status_code(response):
                return
