import aiohttp
import dateutil.parser

from virtool_workflow.api.errors import InsufficientJobRights, JobsAPIServerError, NotFound
from virtool_workflow.data_model.analysis import Analysis
from virtool_workflow.data_model.files import AnalysisFile


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
            raise JobsAPIServerError(await response.text(), response.status)
        except KeyError:
            if response.status == 203:
                raise InsufficientJobRights(response_json, response.status)
            elif response.status == 404:
                raise NotFound(response_json, response.status)
