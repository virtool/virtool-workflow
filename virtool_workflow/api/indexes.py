from pathlib import Path

import aiohttp
import dateutil.parser

from virtool_workflow.abc.data_providers import AbstractIndexProvider
from virtool_workflow.analysis.indexes import Index
from virtool_workflow.api.errors import raising_errors_by_status_code
from virtool_workflow.data_model import Reference
from virtool_workflow.data_model.files import VirtoolFileFormat, VirtoolFile
from virtool_workflow.execution.run_in_executor import FunctionExecutor
from virtool_workflow.execution.run_subprocess import RunSubprocess


async def _fetch_reference(ref_id, http, jobs_api_url):
    async with http.get(f"{jobs_api_url}/references/{ref_id}") as response:
        async with raising_errors_by_status_code(response) as reference_json:
            return Reference(
                reference_json["id"],
                reference_json["data_type"],
                reference_json["description"],
                reference_json["name"],
                reference_json["organism"],
            )


class IndexProvider(AbstractIndexProvider):
    """
    Provide access to Virtool's indexes via the Jobs API.

    :param index_id: The index ID for the current job.
    :param ref_id: The reference ID for the current job.
    :param index_path: The file system path to store index files.
    :param http: An :obj:`aiohttp.ClientSession` to use when making HTTP requests.
    :param jobs_api_url: The base URL for the jobs API (should include `/api`).
    :param run_in_executor: A :class:`FunctionExecutor` to use for background operations.
    :param run_subprocess: A :class:`RunSubprocess` function to use for subprocesses.
    """

    def __init__(self,
                 index_id: str,
                 ref_id: str,
                 index_path: Path,
                 http: aiohttp.ClientSession,
                 jobs_api_url: str,
                 run_in_executor: FunctionExecutor,
                 run_subprocess: RunSubprocess):
        self._index_id = index_id
        self._ref_id = ref_id
        self.index_path = index_path
        self.http = http
        self.jobs_api_url = jobs_api_url
        self.run_in_executor = run_in_executor
        self.run_subprocess = run_subprocess

    async def get(self) -> Index:
        """Get the index for the current job."""
        async with self.http.get(f"{self.jobs_api_url}/indexes/{self._index_id}") as response:
            async with raising_errors_by_status_code(response) as index_document:
                return Index(
                    index_document["id"],
                    index_document["manifest"],
                    self.index_path,
                    await _fetch_reference(self._ref_id, self.http, self.jobs_api_url),
                    self.run_in_executor,
                    self.run_subprocess,
                )

    async def upload(self, path: Path, format: VirtoolFileFormat = "fasta") -> VirtoolFile:
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
        :param format: The format of the file.
        :return: A :class:`VirtoolFile` object.
        """
        with path.open('rb') as f:
            async with self.http.post(f"{self.jobs_api_url}/indexes/{self._index_id}/files",
                                      data={"file": f},
                                      params={"name": path.name}) as response:
                async with raising_errors_by_status_code(response, accept=[201]) as file_json:
                    return VirtoolFile(
                        id=file_json["id"],
                        name=file_json["name"],
                        size=file_json["size"],
                        format=file_json["format"],
                        name_on_disk=file_json["name_on_disk"],
                        uploaded_at=dateutil.parser.isoparse(file_json["uploaded_at"])
                    )

    async def finalize(self):
        raise NotImplementedError()
