from abc import ABC, abstractmethod


class AbstractIndexProvider(ABC):

    @abstractmethod
    def set_has_json(self):
        """Mark that the index associated with the current job has a json representation of the reference available."""
        ...
