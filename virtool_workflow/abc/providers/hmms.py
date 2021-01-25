from abc import ABC, abstractmethod
from typing import List
from virtool_workflow.data_model import HMM


class AbstractHmmsProvider(ABC):

    @property
    @abstractmethod
    def hmm_list(self) -> List[HMM]:
        ...
