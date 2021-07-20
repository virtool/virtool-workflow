import asyncio
import shutil
from pathlib import Path

import aiohttp
from virtool_workflow.api.errors import (JobsAPIServerError, NotFound,
                                         raising_errors_by_status_code)
from virtool_workflow.api.utils import (read_file_from_response,
                                        upload_file_via_put)
from virtool_workflow.caching.caches import (Cache, Caches,
                                             CacheWriter, ReadsCache)
from virtool_workflow.data_model.files import VirtoolFileFormat
from virtool_workflow.execution.run_in_executor import FunctionExecutor


class CacheAlreadyOpen(Exception):
    pass


class RemoteReadsCacheWriter(CacheWriter[ReadsCache]):

    def __init__(self, key, path, sample_id, http, jobs_api_url, run_in_executor):
        super(RemoteReadsCacheWriter, self).__init__(key, path)
        self.http = http
        self.sample_id = sample_id
        self.url = f"{jobs_api_url}/samples/{sample_id}/caches"
        self.run_in_executor = run_in_executor

    async def open(self):
        """
        Create a new cache if one does not exist.

        :raise CacheAlreadyOpen: When there is an existing cache.
        :raise NotFound: When `.sample_id` does not identify a sample.
        :raise JobsAPIServerError: When there is any unexpected status code in the server's response.
        """
        response = await self.http.post(self.url, json={
            "key": self.key
        })

        if response.status == 201:
            return

        if response.status == 409:
            raise CacheAlreadyOpen(self.key)
        elif response.status == 404:
            raise NotFound(self.sample_id)
        else:
            raise JobsAPIServerError(response.status)

    async def upload(self, path: Path, format_: VirtoolFileFormat = "fastq"):
        """Upload a file to the cache."""
        await self.run_in_executor(shutil.copyfile, path, self.path / path.name)

        if path.name in ("reads_1.fq.gz", "reads_2.fq.gz"):
            return await upload_file_via_put(self.http,
                                             f"{self.url}/{self.key}/reads/{path.name}",
                                             path,
                                             params={})

        return await upload_file_via_put(self.http, f"{self.url}/{self.key}/artifacts", path, params={
            "name": path.name,
            "type": format_,
        })

    async def close(self):
        """Finalize the cache."""
        await super(RemoteReadsCacheWriter, self).close()

        response = await self.http.patch(f"{self.url}/{self.key}", json={
            "quality": self.cache.quality
        })

        if response.status != 200:
            raise JobsAPIServerError(response.status)

    async def delete(self):
        """Delete the cache."""
        response = await self.http.delete(f"{self.url}/{self.key}")
        async with raising_errors_by_status_code(response, accept=[204]):
            pass


class RemoteReadCaches(Caches[ReadsCache]):
    def __init__(
            self,
            sample_id: str,
            paired: bool,
            path: Path,
            http: aiohttp.ClientSession,
            jobs_api_url: str,
            run_in_executor: FunctionExecutor,
            poll_rate: int = 5,
    ):
        self.sample_id = sample_id
        self.paired = paired
        self.path = path
        self.http = http
        self.url = f"{jobs_api_url}/samples/{self.sample_id}/caches"
        self.jobs_api_url = jobs_api_url
        self.run_in_executor = run_in_executor
        self.poll_rate = poll_rate

    async def get(self, key: str) -> ReadsCache:
        """
        Get the cache with the given key.

        If a cache exists, but is not ready, this method will not return until the
        cache is ready. This occurs when multiple instances of a workflow are attempting
        to create a cache with the same key.
        """
        response = await self.http.get(f"{self.url}/{key}")

        if response.status == 404:
            raise KeyError(key)

        if response.status != 200:
            raise JobsAPIServerError(response.status)

        cache = await response.json()

        if cache["ready"] is not True:
            # Continually request cache until it is ready.
            await asyncio.sleep(self.poll_rate)
            return await self.get(key)

        cache_path = self.path / key
        cache_path.mkdir()

        files = ("reads_1.fq.gz", "reads_2.fq.gz") if self.paired else (
            "reads_1.fq.gz",)

        for filename in files:
            response = await self.http.get(f"{self.url}/{key}/reads/{filename}")
            await read_file_from_response(response, cache_path)

        return ReadsCache(
            key=key,
            path=cache_path,
            quality=cache["quality"],
        )

    def create(self, key: str) -> CacheWriter[Cache]:
        """Create a new cache writer."""
        cache_path = self.path / key
        cache_path.mkdir()
        return RemoteReadsCacheWriter(key, cache_path, self.sample_id,
                                      self.http, self.jobs_api_url, self.run_in_executor)
