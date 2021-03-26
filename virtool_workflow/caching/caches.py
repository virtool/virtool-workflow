from abc import abstractmethod
from inspect import signature
from typing import TypeVar

from virtool_workflow.abc.caches.cache import Cache, AbstractCacheWriter, CacheNotFinalized, AbstractCaches

GenericCache = TypeVar("GenericCache", bound=Cache)


class GenericCacheWriter(AbstractCacheWriter):
    """
    A :class:`AbstractCacheWriter` which supports attribute assignment based on a
    type argument extending :class:`Cache`.

    This class will have attributes for each parameter in the signature of the :func:`__init__`
    method of the class given as a type argument.
    """

    def __init_subclass__(cls, cache_class: GenericCache = None, **kwargs):
        if cache_class is not None:
            cls.cache_class = cache_class
        super(GenericCacheWriter, cls).__init_subclass__(**kwargs)

    def __init__(self, key, path):
        self._expected_attrs = list(signature(self.cache_class.__init__).parameters)[1:]

        for key_ in self._expected_attrs:
            setattr(self, key_, None)

        self.key = key
        self.path = path

        self._cache = None

    @property
    def cache(self) -> GenericCache:
        if not self._cache:
            missing_keys = [key for key in self._expected_attrs if getattr(self, key) is None]
            if missing_keys:
                raise CacheNotFinalized(
                    f"Cache has missing attributes: {missing_keys}"
                )
            else:
                raise AttributeError("cache")
        return self._cache

    async def write(self) -> GenericCache:
        """Create an instance of the cache class using the applicable attributes of this :class:`GenericCacheWriter`."""
        self._cache = self.cache_class(**{key: getattr(self, key) for key in self._expected_attrs})
        return self._cache

    async def open(self):
        """Default implementation of :func:`.open()`"""
        return self

    async def close(self):
        """Create the cache object before closing this :class:`AbstractCacheWriter`"""
        await self.write()
        return await super(GenericCacheWriter, self).close()

    def __class_getitem__(cls, item):
        """Set the cache_class."""

        class _Temp(cls, cache_class=item):
            ...

        _Temp.__name__ = f"{cls.__name__}[{item.__name__}]"

        return _Temp


class GenericCaches(AbstractCaches):
    cache_class = Cache

    @abstractmethod
    async def get(self, key: str) -> GenericCache:
        pass

    @abstractmethod
    def create(self, key: str) -> GenericCacheWriter[GenericCache]:
        pass

    def __class_getitem__(cls, item):
        """Set the cache_class."""
        cls.cache_class = item
        return cls
