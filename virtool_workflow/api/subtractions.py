import asyncio
from numbers import Number
from pathlib import Path

from aiohttp import ClientSession
from structlog import get_logger

from virtool_workflow.api.errors import raising_errors_by_status_code
from virtool_workflow.api.utils import read_file_from_response, upload_file_via_put
from virtool_workflow.data_model.subtractions import WFSubtraction

logger = get_logger("api")


class SubtractionProvider:
    """
    Operations on a Subtraction via the Jobs API.

    :param subtraction_id: The ID of the subtraction.
    :param http: An class:`aiohttp.ClientSession` to use when making requests.
    :param jobs_api_connection_string: The url for the jobs API.
    :param subtraction_work_path: The working path for subtraction files.
    """

    def __init__(
        self,
        subtraction_id: str,
        http: ClientSession,
        jobs_api_connection_string: str,
        subtraction_work_path: Path,
    ):
        self.subtraction_id = subtraction_id
        self.http = http
        self.api_url = f"{jobs_api_connection_string}/subtractions/{subtraction_id}"
        self.path = subtraction_work_path / subtraction_id

    async def get(self) -> WFSubtraction:
        async with self.http.get(self.api_url) as response:
            async with raising_errors_by_status_code(response) as subtraction_json:
                logger.info("Fetched subtraction", id=self.subtraction_id)
                return WFSubtraction(**subtraction_json, path=self.path)

    async def upload(self, path: Path):
        """
        Upload a file relating to this subtraction.

        Filenames must be one of:
            - subtraction.fa.gz
            - subtraction.1.bt2
            - subtraction.2.bt2
            - subtraction.3.bt2
            - subtraction.4.bt2
            - subtraction.rev.1.bt2
            - subtraction.rev.2.bt2

        :param path: The path to the file

        """
        filename = path.name

        log = logger.bind(id=self.subtraction_id, filename=filename)

        log.info("Uploading subtraction file")

        file = await upload_file_via_put(
            self.http, f"{self.api_url}/files/{path.name}", path
        )

        log.info("Completed subtraction file upload")

        return file

    async def finalize(self, gc: dict[str, Number], count: int):
        """
        Finalize the subtraction by setting the gc.

        :param gc: the nucleotide composition of the subtraction
        :param count: the number of sequences in the FASTA file
        :return: the updated subtraction.
        """
        async with self.http.patch(
            self.api_url, json={"gc": {"n": 0.0, **gc}, "count": count}
        ) as response:
            async with raising_errors_by_status_code(response) as subtraction_json:
                logger.info("Finalized subtraction", id=self.subtraction_id)
                return WFSubtraction(**subtraction_json, path=self.path)

    async def download(self):
        await asyncio.to_thread(self.path.mkdir, parents=True, exist_ok=True)

        names = [
            "subtraction.fa.gz",
            "subtraction.1.bt2",
            "subtraction.2.bt2",
            "subtraction.3.bt2",
            "subtraction.4.bt2",
            "subtraction.rev.1.bt2",
            "subtraction.rev.2.bt2",
        ]

        log = logger.bind(id=self.subtraction_id)

        log.info("Downloading subtraction files")

        for name in names:
            async with self.http.get(f"{self.api_url}/files/{name}") as response:
                await read_file_from_response(response, self.path / name)

        log.info("Completed subtraction file download")

        return self.path

    async def delete(self):
        """Delete the subtraction."""
        async with self.http.delete(self.api_url) as response:
            async with raising_errors_by_status_code(response, accept=[204]):
                ...
