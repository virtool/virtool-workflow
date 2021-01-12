from abc import ABC, abstractmethod
from typing import Dict, Any


class AbstractIndexProvider(ABC):

    @abstractmethod
    def store_sequence_otu_map(self, sequence_otu_map: Dict[str, Any]):
        """Store the sequence_otu_map for the current job."""
        ...

    @abstractmethod
    def set_has_json(self):
        """Mark that the index associated with the current job has a json representation of the reference available."""
        ...
