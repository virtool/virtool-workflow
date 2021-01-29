from abc import ABC, abstractmethod
from typing import Dict
from numbers import Number


class AbstractSubtractionProvider(ABC):

    @abstractmethod
    async def store_count_and_gc(self, count: int, gc: Dict[str, Number]):
        """Store the count and gc for the current subtraction and mark it as ready."""
        ...

    @abstractmethod
    async def delete(self):
        """Permanently delete the subtraction."""

