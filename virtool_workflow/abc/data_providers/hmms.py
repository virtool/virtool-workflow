from abc import ABC, abstractmethod
from typing import List
from virtool_workflow.data_model import HMM


class AbstractHmmsProvider(ABC):

    @abstractmethod
    async def hmm_list(self) -> List[HMM]:
        ...
