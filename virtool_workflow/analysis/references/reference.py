from typing import Dict, Any

from virtool_workflow import fixture
from virtool_workflow.abc.db import AbstractDatabase


@fixture
def reference(job_args: Dict[str, Any], database: AbstractDatabase):
    """The reference document for the current job."""
    return database.fetch_document_by_id(job_args["ref_id"], "references")

