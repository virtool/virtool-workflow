from abc import ABC, abstractmethod
from typing import Dict, Any

from virtool_workflow.data_model.analysis import Analysis
from virtool_workflow.data_model.files import AnalysisFile


class AbstractAnalysisProvider(ABC):

    @abstractmethod
    async def get(self) -> Analysis:
        ...

    @abstractmethod
    async def upload(self, file: AnalysisFile):
        ...

    @abstractmethod
    async def download(self, file_id):
        ...

    @abstractmethod
    async def store_result(self, result: Dict[str, Any]):
        """
        Set the result for the current job and mark it as ready.

        :param result: A dict representing the results of the current workflow.
        """
        ...

    @abstractmethod
    async def delete(self):
        """Delete the analysis for the current job."""
        ...

    def __await__(self):
        return self.get().__await__()
