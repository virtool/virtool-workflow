from numbers import Number
from pathlib import Path
from typing import Dict

import aiohttp

from virtool_workflow.abc.data_providers import AbstractSubtractionProvider
from virtool_workflow.api.errors import raising_errors_by_status_code
from virtool_workflow.data_model import Subtraction, NucleotideComposition


class SubtractionProvider(AbstractSubtractionProvider):

    def __init__(
            self,
            subtraction_id: str,
            http: aiohttp.ClientSession,
            jobs_api_url: str,
            subtraction_work_path: Path,
    ):
        self.subtraction_id = subtraction_id
        self.http = http
        self.api_url = f"{jobs_api_url}/subtractions/{subtraction_id}"
        self.path = subtraction_work_path

    async def get(self) -> Subtraction:
        async with self.http.get(self.api_url) as response:
            async with raising_errors_by_status_code(response) as subtraction_json:
                return Subtraction(
                    subtraction_json["id"],
                    subtraction_json["name"],
                    subtraction_json["nickname"],
                    subtraction_json["count"],
                    subtraction_json["deleted"],
                    NucleotideComposition(**subtraction_json["gc"]),
                    subtraction_json["is_host"],
                    self.path,
                )

    async def finalize(self, count: int, gc: Dict[str, Number]):
        pass

    async def delete(self):
        pass
