from pathlib import Path

import aiofiles

from virtool_workflow.api.errors import raising_errors_by_status_code


async def read_file_from_response(response, target_path: Path):
    async with raising_errors_by_status_code(response, accept=[201]):
        async with aiofiles.open(target_path, "wb") as f:
            await f.write(await response.read())

    return target_path
