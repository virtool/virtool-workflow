import aiohttp

from virtool_workflow.abc.data_providers import AbstractIndexProvider
from virtool_workflow.data_model import Index
from virtool_workflow.api.


class IndexProvider(AbstractIndexProvider):
    def __init__(self, index_id: str, ref_id: str, http: aiohttp.ClientSession, jobs_api_url: str):
        self._index_id = index_id
        self._ref_id = ref_id
        self.http = http
        self.jobs_api_url = jobs_api_url

    async def get(self) -> Index:
        async with self.http.get(f"{self.jobs_api_url}/indexes/{self._index_id}") as response:
            index_document = await response.json()

    async def finalize(self):
        raise NotImplementedError()
