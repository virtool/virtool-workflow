import logging
import pprint
from pathlib import Path
from typing import Dict, Any

import aiohttp

from virtool_workflow.analysis.utils import ReadPaths, make_read_paths
from virtool_workflow.api.errors import (raising_errors_by_status_code,
                                         AlreadyFinalized,
                                         JobsAPIServerError)
from virtool_workflow.api.utils import (upload_file_via_put,
                                        read_file_from_response)
from virtool_workflow.data_model import Sample
from virtool_workflow.data_model.files import VirtoolFileFormat, VirtoolFile

logger = logging.getLogger(__name__)


async def _make_sample_from_response(response) -> Sample:
    async with raising_errors_by_status_code(response) as sample_json:
        logger.debug(pprint.pformat(sample_json))
        return Sample(
            id=sample_json["id"],
            name=sample_json["name"],
            host=sample_json["host"],
            isolate=sample_json["isolate"],
            locale=sample_json["locale"],
            library_type=sample_json["library_type"],
            paired=sample_json["paired"],
            quality=sample_json["quality"],
            nuvs=sample_json["nuvs"],
            pathoscope=sample_json["pathoscope"],
            files=sample_json["files"] if "files" in sample_json else [],
        )


class SampleProvider:

    def __init__(self,
                 sample_id: str,
                 http: aiohttp.ClientSession,
                 jobs_api_url: str):
        self.id = sample_id
        self.http = http
        self.url = f"{jobs_api_url}/samples/{sample_id}"

    async def get(self) -> Sample:
        async with self.http.get(self.url) as response:
            logger.info("Fetched sample document")
            return await _make_sample_from_response(response)

    async def finalize(self, quality: Dict[str, Any]) -> Sample:
        async with self.http.patch(self.url, json={"quality": quality}) as response:
            return await _make_sample_from_response(response)

    async def delete(self):
        async with self.http.delete(self.url) as response:
            async with raising_errors_by_status_code(response, accept=[204], status_codes_to_exceptions={
                400: AlreadyFinalized,
                500: JobsAPIServerError
            }):
                pass

    async def upload(self, path: Path, format: VirtoolFileFormat = "fastq") -> VirtoolFile:
        if path.name in ("reads_1.fq.gz", "reads_2.fq.gz"):
            return await upload_file_via_put(self.http, f"{self.url}/reads/{path.name}", path, params={})

        return await upload_file_via_put(self.http, f"{self.url}/artifacts", path, params={
            "name": path.name,
            "type": format
        })

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
