from abc import ABC, abstractmethod
from typing import Dict, Any


class AbstractOTUsProvider(ABC):

    @abstractmethod
    def fetch_otus_for_reference(self):
        """Fetch the OTUs associated with the current reference."""
        ...

    @abstractmethod
    async def update_last_indexed_versions(self, *ids):
        """Update the last indexed version for each OTU to the current version."""
        ...

    @abstractmethod
    async def patch_to_version(self, otu: Dict[str, Any], version: str) -> Dict[str, Any]:
        """
        Patch an out document to a specific version.

        :param otu: The otu document to patch
        :param version: The version to patch the otu document to
        :return: The patched otu document
        """