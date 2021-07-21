from abc import abstractmethod
from inspect import signature
from dataclasses import dataclass
from pathlib import Path


class CacheNotFinalized(Exception):
    ...


class CacheExists(Exception):
    ...


@dataclass
class Cache:
    """Base class for all caches."""
    key: str
    path: Path


@dataclass
class ReadsCache(Cache):
    quality: dict


class CacheWriter:
    """
    A :class:`AbstractCacheWriter` which supports attribute assignment based on a
    type argument extending :class:`Cache`.

    This class will have attributes for each parameter in the signature of the :func:`__init__`
    method of the class given as a type argument.
    """

    def __init_subclass__(cls, cache_class: Cache = None, **kwargs):
        if cache_class is not None:
            cls.cache_class = cache_class
        super(CacheWriter, cls).__init_subclass__(**kwargs)

    def __init__(self, key, path):
        self._expected_attrs = list(
            signature(self.cache_class.__init__).parameters)[1:]

        for key_ in self._expected_attrs:
            setattr(self, key_, None)

        self.key = key
        self.path = path

        self._cache = None

    @property
    def cache(self) -> Cache:
        if not self._cache:
            missing_keys = [
                key for key in self._expected_attrs if getattr(self, key) is None]
            if missing_keys:
                raise CacheNotFinalized(
                    f"Cache has missing attributes: {missing_keys}"
                )
            else:
                raise AttributeError("cache")
        return self._cache

    async def write(self) -> Cache:
        """Create an instance of the cache class using the applicable attributes of this :class:`CacheWriter`."""
        self._cache = self.cache_class(
            **{key: getattr(self, key) for key in self._expected_attrs})
        return self._cache

    async def open(self):
        """Default implementation of :func:`.open()`"""
        return self

    async def close(self):
        """Create the cache object before closing this :class:`CacheWriter`"""
        await self.write()

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, traceback):
        if exc_val:
            return await self.delete()

        try:
            return await self.close()
        except Exception as e:
            await self.delete()
            raise e

    def __class_getitem__(cls, item):
        """Set the cache_class."""

        class _Temp(cls, cache_class=item):
            ...

        _Temp.__name__ = f"{cls.__name__}[{item.__name__}]"

        return _Temp


class Caches:
    cache_class = Cache

    @abstractmethod
    async def get(self, key: str) -> Cache:
        pass

    @abstractmethod
    def create(self, key: str) -> CacheWriter:
        pass

    def __class_getitem__(cls, item):
        """Set the cache_class."""
        cls.cache_class = item
        return cls
