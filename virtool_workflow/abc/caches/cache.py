from abc import abstractmethod, ABC
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from pathlib import Path


class CacheExists(Exception):
    ...


class CacheFileMissing(ValueError):
    ...


class CacheNotFinalized(ValueError):
    ...


@dataclass
class Cache:
    key: str
    path: Path


class AbstractCacheWriter(AbstractAsyncContextManager):

    @property
    @abstractmethod
    def cache(self) -> Cache:
        """
        The cache which was created by this :class:`AbstractCacheWriter`.

        :raises CacheNotFinalized: When this property is accessed before the cache has been finalized.
        """

    @abstractmethod
    async def open(self):
        """
        Signal intent to create a new cache.

        :raises CacheExists: When there is already a cache open with a key matching :obj:`self.key`.
        """
        ...

    @abstractmethod
    async def upload(self, path: Path):
        """
        Upload a file to this cache.

        :param path: The path to a file to upload.
        :raises FileExistsError: When there is already a file in the cache with the same name.
        :raises IsADirectoryError: When the path given is a directory.
        """

        ...

    @abstractmethod
    async def close(self):
        """
        Finalize the cache.

        This method should call :func:`.delete` in the case of an invalid cache.

        :raises ValueError: When a required value of the cache has not been set.
        :raises CacheFileMissing: When a required file for the cache has not been uploaded.
        """
        ...

    @abstractmethod
    async def delete(self):
        """Delete the cache."""
        ...

    async def __aenter__(self) -> "AbstractCacheWriter":
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            return await self.delete()

        return await self.close()


class AbstractCaches(ABC):

    @abstractmethod
    async def get(self, key: str) -> Cache:
        """
        Get the cache with a given key.

        :raises KeyError: When the given key does not map to an existing cache.
        """

    @abstractmethod
    def create(self, key: str) -> AbstractCacheWriter:
        """Create a new cache.

        :raises CacheExists: When a cache already exists for the given key.
        """
        ...

    @abstractmethod
    def __contains__(self, item: str):
        """Check if there is an existing cache with the given key."""
        ...
