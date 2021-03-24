import shutil
from pathlib import Path

from virtool_workflow.abc.caches.analysis_caches import ReadsCache
from virtool_workflow.api.errors import NotFound, JobsAPIServerError, raising_errors_by_status_code
from virtool_workflow.api.utils import upload_file_via_post, upload_file_via_put
from virtool_workflow.caching.caches import GenericCacheWriter
from virtool_workflow.data_model.files import VirtoolFileFormat


class CacheAlreadyOpen(Exception):
    pass


class RemoteReadsCacheWriter(GenericCacheWriter[ReadsCache]):

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

        return await upload_file_via_post(self.http, f"{self.url}/{self.key}/artifacts", path, params={
            "name": path.name,
            "type": format_,
        })

    async def close(self):
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
