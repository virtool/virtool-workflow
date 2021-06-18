from dataclasses import dataclass
from pathlib import Path

import pytest

from virtool_workflow.abc.caches.cache import Cache, CacheExists
from virtool_workflow.caching.local import LocalCacheWriter, LocalCaches


@dataclass
class MockCache(Cache):
    foo: str
    bar: str


@pytest.fixture
def local_caches(tmpdir, run_in_executor):
    return LocalCaches[MockCache](Path(tmpdir), run_in_executor)


@pytest.fixture
def foo_txt(tmpdir):
    mock_file = Path(tmpdir) / "to_upload/foo.txt"
    mock_file.parent.mkdir()
    mock_file.touch()
    return mock_file


async def test_writer(tmpdir, run_in_executor, foo_txt):
    tmpdir = Path(tmpdir)
    writer = LocalCacheWriter[MockCache]("test_cache", tmpdir, run_in_executor)

    async with writer:
        await writer.upload(foo_txt)
        writer.foo = "bar"
        writer.bar = "foo"

    assert writer.cache.foo == "bar"
    assert writer.cache.bar == "foo"
    assert (writer.cache.path / "foo.txt").exists()


async def test_local_caches(tmpdir, local_caches, foo_txt):
    with pytest.raises(KeyError):
        await local_caches.get("test_cache")

    async with local_caches.create("test_cache") as cache:
        cache.foo = "foo"
        cache.bar = "bar"
        await cache.upload(foo_txt)

    with pytest.raises(CacheExists):
        async with local_caches.create("test_cache"):
            ...

    cache = await local_caches.get("test_cache")

    assert cache.foo == "foo"
    assert cache.bar == "bar"

    assert isinstance(cache, MockCache)


async def test_local_caches_delete_on_error(local_caches):
    with pytest.raises(Exception):
        async with local_caches.create("test_cache") as cache:
            raise Exception()

    with pytest.raises(KeyError):
        await local_caches.get("test_cache")

    assert not (local_caches.path / "test_cache").exists()
