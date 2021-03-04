from numbers import Number
from typing import Dict

from virtool_workflow.abc.data_providers import AbstractSubtractionProvider
from virtool_workflow.data_model import Subtraction


class SubtractionProvider(AbstractSubtractionProvider):
    async def get(self) -> Subtraction:
        pass

    async def finalize(self, count: int, gc: Dict[str, Number]):
        pass

    async def delete(self):
        pass
