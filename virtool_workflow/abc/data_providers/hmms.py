from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from virtool_workflow.data_model import HMM


class AbstractHMMsProvider(ABC):

    @abstractmethod
    async def get(self, hmm_id: str):
        """Get the HMM annotation with the given ID."""
        ...

    @abstractmethod
    async def hmm_list(self) -> List[HMM]:
        """Get a list of all HMM annotations."""
        ...

    @abstractmethod
    async def get_profiles(self) -> Path:
        """Get the profiles.hmm file."""
        ...
