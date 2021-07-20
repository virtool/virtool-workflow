import gzip
import json
import shutil
from pathlib import Path
from typing import List

import aiofiles
import aiohttp
from virtool_core.utils import decompress_file

from virtool_workflow.api.errors import raising_errors_by_status_code
from virtool_workflow.api.utils import read_file_from_response
from virtool_workflow.data_model import HMM


def _hmm_from_dict(hmm_json) -> HMM:
    return HMM(
        id=hmm_json["id"],
        cluster=hmm_json["cluster"],
        count=hmm_json["count"],
        entries=hmm_json["entries"],
        families=hmm_json["families"],
        genera=hmm_json["genera"],
        hidden=hmm_json["hidden"] if "hidden" in hmm_json else False,
        length=hmm_json["length"],
        mean_entropy=hmm_json["mean_entropy"],
        total_entropy=hmm_json["total_entropy"],
        names=hmm_json["names"],
    )


class HMMsProvider:

    def __init__(self,
                 http: aiohttp.ClientSession,
                 jobs_api_url: str,
                 work_path: Path,
                 number_of_processes: int = 3):
        self.http = http
        self.url = f"{jobs_api_url}/hmms"
        self.path = work_path / "hmms"
        self.number_of_processes = number_of_processes

        self.path.mkdir(parents=True, exist_ok=True)

    async def get(self, hmm_id: str):
        async with self.http.get(f"{self.url}/{hmm_id}") as response:
            async with raising_errors_by_status_code(response) as hmm_json:
                return _hmm_from_dict(hmm_json)

    async def hmm_list(self) -> List[HMM]:
        async with self.http.get(f"{self.url}/files/annotations.json.gz") as response:
            await read_file_from_response(response, self.path / "annotations.json.gz")

        try:
            decompress_file(str(self.path / "annotations.json.gz"),
                            str(self.path / "annotations.json"),
                            self.number_of_processes)
        except gzip.BadGzipFile:
            shutil.copyfile(self.path / "annotations.json.gz",
                            self.path / "annotations.json")

        async with aiofiles.open(self.path / "annotations.json") as f:
            hmms_json = json.loads(await f.read())
            return [_hmm_from_dict(hmm) for hmm in hmms_json]

    async def get_profiles(self) -> Path:
        async with self.http.get(f"{self.url}/files/profiles.hmm") as response:
            async with raising_errors_by_status_code(response, accept=[200]):
                async with aiofiles.open(self.path / "profiles.hmm", "wb") as f:
                    await f.write(await response.read())

        return self.path / "profiles.hmm"
