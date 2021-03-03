from abc import ABC, abstractmethod

from virtool_workflow.data_model import Index


class AbstractIndexProvider(ABC):

    @abstractmethod
    async def get(self) -> Index:
        """Get the current index."""
        ...

    @abstractmethod
    async def finalize(self):
        """Mark that the index associated with the current job has a json representation of the reference available."""
        ...

    def __await__(self):
        return self.get().__await__()
