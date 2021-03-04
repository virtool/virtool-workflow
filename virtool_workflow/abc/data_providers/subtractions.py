from abc import ABC, abstractmethod
from numbers import Number
from typing import Dict

from virtool_workflow.data_model import Subtraction


class AbstractSubtractionProvider(ABC):

    @abstractmethod
    async def get(self) -> Subtraction:
        """Get the subtraction."""

    @abstractmethod
    async def finalize(self, count: int, gc: Dict[str, Number]):
        """Store the count and gc for the current subtraction and mark it as ready."""
        ...

    @abstractmethod
    async def delete(self):
        """Permanently delete the subtraction."""

    def __await__(self):
        return self.get().__await__()
