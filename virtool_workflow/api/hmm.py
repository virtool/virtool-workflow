import json
from operator import itemgetter
from pathlib import Path
from typing import List

import aiofiles
import aiohttp

from virtool_workflow.abc.data_providers import AbstractHMMsProvider
from virtool_workflow.api.errors import raising_errors_by_status_code
from virtool_workflow.data_model import HMM


def _hmm_from_dict(hmm_json) -> HMM:
    return HMM(

        *itemgetter("id", "cluster", "count", "entries",
                    "families", "genera", "hidden",
                    "length", "mean_entropy",
                    "total_entropy", "names")(hmm_json)
    )


class HMMsProvider(AbstractHMMsProvider):

    def __init__(self,
                 http: aiohttp.ClientSession,
                 jobs_api_url: str,
                 work_path: Path):
        self.http = http
        self.url = f"{jobs_api_url}/hmm"
        self.path = work_path / "hmms"

        self.path.mkdir(parents=True, exist_ok=True)

    async def get(self, hmm_id: str):
        async with self.http.get(f"{self.url}/{hmm_id}") as response:
            async with raising_errors_by_status_code(response) as hmm_json:
                return _hmm_from_dict(hmm_json)

    async def hmm_list(self) -> List[HMM]:
        async with self.http.get(f"{self.url}/files/annotations.json.gz") as response:
            async with raising_errors_by_status_code(response, accept=[200]):
                async with aiofiles.open(self.path / "annotations.json", "wb") as f:
                    await f.write(await response.read())

        async with aiofiles.open(self.path / "annotations.json") as f:
            hmms_json = json.loads(await f.read())
            return [_hmm_from_dict(hmm) for hmm in hmms_json]

    async def get_profiles(self) -> Path:
        async with self.http.get(f"{self.url}/files/profiles.hmm") as response:
            async with raising_errors_by_status_code(response, accept=[200]):
                async with aiofiles.open(self.path / "profiles.hmm", "wb") as f:
                    await f.write(await response.read())

        return self.path / "profiles.hmm"
