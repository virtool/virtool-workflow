from logging import getLogger
from pathlib import Path
from typing import Any, Dict

from aiohttp import ClientSession

from virtool_workflow.analysis.utils import ReadPaths, make_read_paths
from virtool_workflow.api.errors import (
    AlreadyFinalized,
    JobsAPIServerError,
    raising_errors_by_status_code,
)
from virtool_workflow.api.utils import read_file_from_response, upload_file_via_put
from virtool_workflow.data_model.files import VirtoolFile, VirtoolFileFormat
from virtool_workflow.data_model.samples import WFSample

logger = getLogger("api")


class SampleProvider:
    def __init__(
        self,
        sample_id: str,
        http: ClientSession,
        jobs_api_connection_string: str,
    ):
        self.id = sample_id
        self.http = http
        self._api_connection_string = jobs_api_connection_string

    @property
    def url(self):
        return f"{self._api_connection_string}/samples/{self.id}"

    async def get(self) -> WFSample:
        async with self.http.get(self.url) as resp:
            async with raising_errors_by_status_code(resp) as resp_json:
                logger.info(f"Fetched sample document id={self.id}")
                return WFSample(**resp_json)

    async def finalize(self, quality: Dict[str, Any]) -> WFSample:
        async with self.http.patch(self.url, json={"quality": quality}) as resp:
            async with raising_errors_by_status_code(resp) as resp_json:
                return WFSample(**resp_json)

    async def delete(self):
        async with self.http.delete(self.url) as response:
            async with raising_errors_by_status_code(
                response,
                accept=[204],
                status_codes_to_exceptions={
                    400: AlreadyFinalized,
                    500: JobsAPIServerError,
                },
            ):
                pass

    async def upload(self, path: Path, fmt: VirtoolFileFormat = "fastq") -> VirtoolFile:
        if path.name in ("reads_1.fq.gz", "reads_2.fq.gz"):
            return await upload_file_via_put(
                self.http, f"{self.url}/reads/{path.name}", path, params={}
            )

        return await upload_file_via_put(
            self.http,
            f"{self.url}/artifacts",
            path,
            params={"name": path.name, "type": fmt},
        )

    async def download_reads(self, target_path: Path, paired: bool = None) -> ReadPaths:
        if paired is None:
            sample = await self.get()
            paired = sample.paired

        async with self.http.get(f"{self.url}/reads/reads_1.fq.gz") as response:
            await read_file_from_response(response, target_path / "reads_1.fq.gz")

        if paired:
            async with self.http.get(f"{self.url}/reads/reads_2.fq.gz") as response:
                await read_file_from_response(response, target_path / "reads_2.fq.gz")

        return make_read_paths(target_path, paired)

    async def download_artifact(self, filename: str, target_path: Path):
        async with self.http.get(f"{self.url}/artifacts/{filename}") as response:
            await read_file_from_response(response, target_path / filename)
