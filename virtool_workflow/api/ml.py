"""A data provider for ML models."""
from aiohttp import ClientSession


class MLProvider:
    def __init__(self, http: ClientSession, jobs_api_connection_string: str):
        self.http = http
        self.url = f"{jobs_api_connection_string}/ml"

    async def get(self, model_id: str):
        async with self.http.get(f"{self.url}/ml/{model_id}") as response:
            resp = await response.json()

        return MLMo
