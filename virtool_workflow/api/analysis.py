import logging
from pathlib import Path
from typing import Iterable, Tuple, Dict, Any

import aiohttp
import dateutil.parser

from virtool_workflow.abc.data_providers import AbstractAnalysisProvider
from virtool_workflow.api.errors import InsufficientJobRights, JobsAPIServerError, NotFound
from virtool_workflow.data_model.analysis import Analysis
from virtool_workflow.data_model.files import AnalysisFile, VirtoolFileFormat
from virtool_workflow.uploads.files import FileUpload

logger = logging.getLogger(__name__)


def _analysis_file_from_api_response_json(json):
    return [
        AnalysisFile(
            id=f["id"],
            name=f["name"],
            name_on_disk=f["name_on_disk"],
            size=f["size"],
            uploaded_at=dateutil.parser.isoparse(f["uploaded_at"]),
            format=f["format"]
        )
        for f in json["files"]
    ]


async def get_analysis_by_id(analysis_id: str, http: aiohttp.ClientSession, jobs_api_url: str) -> Analysis:
    """
    Get the analysis by id via the jobs API.

    :param analysis_id: The id of the analysis.
    :param http: A :class:`aiohttp.ClientSession` instance.
    :param jobs_api_url: The url for the jobs API server.

    :return: A :class:`virtool_workflow.data_model.analysis.Analysis` instance.

    :raise JobsAPIServerError: When the jobs API server fails to respond with a JSON body
    :raise InsufficientJobRights: When the current job does not have sufficient rights to access the analysis.
    :raise NotFound: When the given :obj:`analysis_id` does not correspond to an existing analysis (HTTP 404).
    """
    async with http.get(f"{jobs_api_url}/analyses/{analysis_id}") as response:
        try:
            response_json = await response.json()

            return Analysis(
                id=response_json["id"],
                files=_analysis_file_from_api_response_json(response_json),
            )
        except aiohttp.ContentTypeError:
            raise JobsAPIServerError(response.status)
        except KeyError:
            if response.status == 203:
                raise InsufficientJobRights(response_json, response.status)
            elif response.status == 404:
                raise NotFound(response_json, response.status)


async def upload_analysis_file(analysis_id: str,
                               path: Path,
                               format: VirtoolFileFormat,
                               http: aiohttp.ClientSession,
                               jobs_api_url: str):
    """Upload an analysis file using the jobs API."""
    with path.open('rb') as binary:
        async with http.post(f"{jobs_api_url}/analyses/{analysis_id}", data={"file": binary}, query={
            "name": path.name,
            "format": format
        }) as response:
            try:
                response_json = await response.json()
            except aiohttp.ContentTypeError as content_type_error:
                raise JobsAPIServerError(response.status) from content_type_error

            try:
                return AnalysisFile(
                    id=response_json["id"],
                    name=response_json["name"],
                    name_on_disk=response_json["name_on_disk"],
                    size=response_json["size"],
                    uploaded_at=dateutil.parser.isoparse(response_json["uploaded_at"]),
                    format=response_json["format"],
                )
            except KeyError as key_error:
                if response.status in (400, 409):
                    raise ValueError(response_json) from key_error
                elif response.status == 403:
                    raise InsufficientJobRights(response_json) from key_error
                elif response.status == 404:
                    raise NotFound(response_json) from key_error
                else:
                    raise JobsAPIServerError(response_json) from key_error


class AnalysisProvider(AbstractAnalysisProvider):
    def __init__(self, analysis_id, http: aiohttp.ClientSession, jobs_api_url: str):
        self.id = analysis_id
        self.http = http
        self.api_url = jobs_api_url

    async def get(self) -> Analysis:
        return await get_analysis_by_id(self.id, self.http, self.api_url)

    async def upload(self, file: AnalysisFile):
        pass

    async def download(self, file_id):
        pass

    async def store_result(self, result: Dict[str, Any]):
        pass

    async def store_files(self, uploads: Iterable[Tuple[FileUpload, Path]]):
        pass

    async def delete(self):
        pass
