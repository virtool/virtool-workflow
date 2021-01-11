from abc import ABC, abstractmethod


class AbstractReferenceProvider(ABC):
    def fetch_data_type(self) -> str:
        """Get the data type of the reference associated with the current job."""
        ...

    def fetch_organism(self) -> str:
        """Get the organism for the reference associated with the current job."""
        ...

    def fetch_targets(self) -> str:
        """Get the targets for the reference associated with the current job."""
        ...

