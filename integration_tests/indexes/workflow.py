from typing import List

from virtool_workflow import step
from virtool_workflow.data_model.indexes import Index


@step
def fetch_sample(indexes: List[Index]):
    ...
