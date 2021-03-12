from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from pathlib import Path


class AbstractCache(ABC, AbstractAsyncContextManager):
    key: str
    path: Path

    @abstractmethod
    async def open(self) -> "AbstractCache":
        """Signal intent to create a new cache."""
        ...

    @abstractmethod
    async def upload(self, path: Path):
        """Upload a file to this cache"""
        ...

    @abstractmethod
    async def close(self):
        """Finalize the cache."""
        ...

    @abstractmethod
    async def delete(self):
        """Delete the cache."""
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.close()


class AbstractCaches(ABC, AbstractAsyncContextManager):

    @abstractmethod
    async def get(self, key: str) -> AbstractCache:
        """Get the cache with a given key."""

    @abstractmethod
    async def create(self, key: str) -> AbstractCache:
        """Create a new cache."""
        ...
