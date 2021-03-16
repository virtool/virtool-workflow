from pathlib import Path

import aiofiles
import aiohttp
import dateutil.parser

from virtool_workflow.api.errors import raising_errors_by_status_code
from virtool_workflow.data_model.files import VirtoolFileFormat, VirtoolFile


async def read_file_from_response(response, target_path: Path):
    async with raising_errors_by_status_code(response):
        async with aiofiles.open(target_path, "wb") as f:
            await f.write(await response.read())

    return target_path


async def upload_file_via_post(http: aiohttp.ClientSession,
                               url: str,
                               path: Path,
                               format: VirtoolFileFormat = None,
                               params: dict = None):
    if not params:
        params = {"name": path.name}

        if format is not None:
            params.update(format=format)

    with path.open('rb') as binary:
        async with http.post(url, data={"file": binary}, params=params) as response:
            async with raising_errors_by_status_code(response) as response_json:
                return VirtoolFile(
                    id=response_json["id"],
                    name=response_json["name"],
                    name_on_disk=response_json["name_on_disk"],
                    size=response_json["size"],
                    uploaded_at=dateutil.parser.isoparse(response_json["uploaded_at"]),
                    format=response_json["format"],
                )
