from pathlib import Path

import aiohttp

from virtool_workflow.abc.data_providers import AbstractIndexProvider
from virtool_workflow.analysis.indexes import Index
from virtool_workflow.api.errors import raising_errors_by_status_code
from virtool_workflow.data_model import Reference
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

    async def finalize(self):
        raise NotImplementedError()
