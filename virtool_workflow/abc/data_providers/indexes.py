from abc import ABC, abstractmethod
from typing import Dict

from virtool_workflow.data_model import Reference


class AbstractIndexProvider(ABC):

    @abstractmethod
    async def fetch_reference(self) -> Reference:
        """Get the reference associated with the index for the current job."""
        ...

    @abstractmethod
    async def fetch_manifest(self) -> Dict[str, int]:
        """Get the manifest for the index associated with the current job."""

    @abstractmethod
    async def set_has_json(self):
        """Mark that the index associated with the current job has a json representation of the reference available."""
        ...
