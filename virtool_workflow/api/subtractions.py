from numbers import Number
from pathlib import Path
from typing import Dict

import aiohttp

from virtool_workflow.api.errors import raising_errors_by_status_code
from virtool_workflow.api.utils import (read_file_from_response,
                                        upload_file_via_put)
from virtool_workflow.data_model import Subtraction, NucleotideComposition


def subtraction_from_json(subtraction_json: dict, path: Path) -> Subtraction:
    return Subtraction(
        subtraction_json["id"],
        subtraction_json["name"],
        subtraction_json["nickname"],
        subtraction_json["count"] if "count" in subtraction_json else None,
        NucleotideComposition(
            **subtraction_json["gc"]) if "gc" in subtraction_json else {},
        path,
    )


class SubtractionProvider:
    """
    Operations on a Subtraction via the Jobs API.

    :param subtraction_id: The ID of the subtraction.
    :param http: An class:`aiohttp.ClientSession` to use when making requests.
    :param jobs_api_url: The url for the jobs API.
    :param subtraction_work_path: The working path for subtraction files.
    """

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
        self.path = subtraction_work_path / subtraction_id
        if not self.path.exists():
            self.path.mkdir()

    async def get(self) -> Subtraction:
        async with self.http.get(self.api_url) as response:
            async with raising_errors_by_status_code(response) as subtraction_json:
                return subtraction_from_json(subtraction_json, self.path)

    async def upload(self, path: Path):
        """
        Upload a file relating to this subtraction.

        :param path: The path to the file. The filename must be one of:

            - subtraction.fa.gz
            - subtraction.1.bt2
            - subtraction.2.bt2
            - subtraction.3.bt2
            - subtraction.4.bt2
            - subtraction.rev.1.bt2
            - subtraction.rev.2.bt2
        """
        return await upload_file_via_put(self.http, f"{self.api_url}/files/{path.name}", path)

    async def finalize(self, gc: Dict[str, Number], count: int):
        """
        Finalize the subtraction by setting the gc.
        :param gc: The nucleotide composition of the subtraction
        :return: The updated subtraction.
        """
        async with self.http.patch(self.api_url, json={"gc": gc, "count": count}) as response:
            async with raising_errors_by_status_code(response) as subtraction_json:
                return subtraction_from_json(subtraction_json, self.path)

    async def download(self, target_path: Path = None, *names):
        if not names:
            names = [
                "subtraction.fa.gz",
                "subtraction.1.bt2",
                "subtraction.2.bt2",
                "subtraction.3.bt2",
                "subtraction.4.bt2",
                "subtraction.rev.1.bt2",
                "subtraction.rev.2.bt2",
            ]

        if not target_path:
            target_path = self.path

        for name in names:
            async with self.http.get(f"{self.api_url}/files/{name}") as response:
                await read_file_from_response(response, target_path / name)

        return target_path

    async def delete(self):
        """Delete the subtraction."""
        async with self.http.delete(self.api_url) as response:
            async with raising_errors_by_status_code(response, accept=[204]):
                pass

    def __await__(self) -> Subtraction:
        return self.get().__await__()
