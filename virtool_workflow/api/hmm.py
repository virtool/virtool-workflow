import gzip
import json
import shutil
from pathlib import Path
from typing import List

import aiofiles
from aiohttp import ClientSession
from virtool_core.models.hmm import HMM
from virtool_core.utils import decompress_file

from virtool_workflow.api.errors import raising_errors_by_status_code
from virtool_workflow.api.utils import read_file_from_response


class HMMsProvider:
    def __init__(
        self,
        http: ClientSession,
        jobs_api_connection_string: str,
        work_path: Path,
        number_of_processes: int = 3,
    ):
        self.http = http
        self.url = f"{jobs_api_connection_string}/hmms"
        self.path = work_path / "hmms"
        self.number_of_processes = number_of_processes

        self.path.mkdir(parents=True, exist_ok=True)

    async def get(self, hmm_id: str):
        async with self.http.get(f"{self.url}/{hmm_id}") as response:
            async with raising_errors_by_status_code(response) as resp_json:
                return HMM(**resp_json)

    async def hmm_list(self) -> List[HMM]:
        async with self.http.get(f"{self.url}/files/annotations.json.gz") as response:
            await read_file_from_response(response, self.path / "annotations.json.gz")

        try:
            decompress_file(
                self.path / "annotations.json.gz",
                self.path / "annotations.json",
                self.number_of_processes,
            )
        except gzip.BadGzipFile:
            shutil.copyfile(
                self.path / "annotations.json.gz", self.path / "annotations.json"
            )

        async with aiofiles.open(self.path / "annotations.json") as f:
            return [HMM(**hmm) for hmm in json.loads(await f.read())]

    async def get_profiles(self) -> Path:
        async with self.http.get(f"{self.url}/files/profiles.hmm") as response:
            async with raising_errors_by_status_code(response, accept=[200]):
                async with aiofiles.open(self.path / "profiles.hmm", "wb") as f:
                    await f.write(await response.read())

        return self.path / "profiles.hmm"
