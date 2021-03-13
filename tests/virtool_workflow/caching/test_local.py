from dataclasses import dataclass
from pathlib import Path

from virtool_workflow.abc.caches.cache import Cache
from virtool_workflow.caching.local import LocalCacheWriter


@dataclass
class MockCache(Cache):
    foo: str
    bar: str


async def test_writer(tmpdir, run_in_executor):
    tmpdir = Path(tmpdir)
    writer = LocalCacheWriter[MockCache]("test_cache", tmpdir, run_in_executor)

    mock_file = tmpdir / "to_upload/foo.txt"
    mock_file.parent.mkdir()
    mock_file.touch()

    async with writer:
        await writer.upload(mock_file)
        writer.foo = "bar"
        writer.bar = "foo"

    assert writer.cache.foo == "bar"
    assert writer.cache.bar == "foo"
