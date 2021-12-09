from pathlib import Path

import aiohttp

from virtool_workflow.api.errors import raising_errors_by_status_code
from virtool_workflow.api.utils import (read_file_from_response,
                                        upload_file_via_put)
from virtool_workflow.data_model import Reference
from virtool_workflow.data_model.files import VirtoolFile, VirtoolFileFormat
from virtool_workflow.data_model.indexes import Index


async def _fetch_reference(ref_id, http, jobs_api_url):
    async with http.get(f"{jobs_api_url}/refs/{ref_id}") as response:
        async with raising_errors_by_status_code(response) as reference_json:
            return Reference(
                reference_json["id"],
                reference_json["data_type"],
                reference_json["description"],
                reference_json["name"],
                reference_json["organism"],
            )


class IndexProvider:
    """
    Provide access to Virtool's indexes via the Jobs API.

    :param index_id: The index ID for the current job.
    :param ref_id: The reference ID for the current job.
    :param index_path: The file system path to store index files.
    :param http: An :obj:`aiohttp.ClientSession` to use when making HTTP requests.
    :param jobs_api_url: The base URL for the jobs API.
    """

    def __init__(self,
                 index_id: str,
                 ref_id: str,
                 http: aiohttp.ClientSession,
                 jobs_api_url: str):
        self._index_id = index_id
        self._ref_id = ref_id
        self.http = http
        self.jobs_api_url = jobs_api_url

    async def get(self) -> Index:
        """Get the index for the current job."""
        async with self.http.get(f"{self.jobs_api_url}/indexes/{self._index_id}") as response:
            async with raising_errors_by_status_code(response) as index_document:
                return Index(
                    index_document["id"],
                    index_document["manifest"],
                    await _fetch_reference(self._ref_id, self.http, self.jobs_api_url),
                    ready="ready" in index_document and index_document["ready"]
                )

    async def upload(self, path: Path, format_: VirtoolFileFormat = "fasta") -> VirtoolFile:
        """
        Upload a file associated with the current Index.

        Allowed file names are:

            - reference.json.gz
            - reference.fa.gz
            - reference.1.bt2
            - reference.2.bt2
            - reference.3.bt2
            - reference.4.bt4
            - reference.rev.1.bt2
            - reference.rev.2.bt2

        :param path: The path to the file.
        :param format_: The format of the file.
        :return: A :class:`VirtoolFile` object.
        """
        return await upload_file_via_put(
            self.http,
            f"{self.jobs_api_url}/indexes/{self._index_id}/files/{path.name}",
            path, format_
        )

    async def download(self, target_path: Path, *names) -> Path:
        """Download files associated with the current index."""
        if not names:
            names = {
                "otus.json.gz",
                "reference.fa.gz",
                "reference.1.bt2",
                "reference.2.bt2",
                "reference.3.bt2",
                "reference.4.bt2",
                "reference.rev.1.bt2",
                "reference.rev.2.bt2",
            }

        for name in names:
            async with self.http.get(f"{self.jobs_api_url}/indexes/{self._index_id}/files/{name}") as response:
                await read_file_from_response(response, target_path / name)

        return target_path

    async def finalize(self):
        """Finalize the current index."""
        async with self.http.patch(f"{self.jobs_api_url}/indexes/{self._index_id}") as response:
            async with raising_errors_by_status_code(response) as index_document:
                return Index(
                    index_document["id"],
                    index_document["manifest"],
                    await _fetch_reference(self._ref_id, self.http, self.jobs_api_url),
                    ready=index_document["ready"]
                )

    async def delete(self):
        """Delete an un-finished index."""
        async with self.http.delete(f"{self.jobs_api_url}/indexes/{self._index_id}") as response:
            async with raising_errors_by_status_code(response, accept=[200, 204]):
                pass

    def __await__(self) -> Index:
        return self.get().__await__()
