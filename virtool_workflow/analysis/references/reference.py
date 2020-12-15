from typing import Dict, Any

from virtool_workflow import fixture
from virtool_workflow.db import db


@fixture
def reference(job_args: Dict[str, Any]):
    """The reference document for the current job."""
    return db.fetch_document_by_id(job_args["ref_id"], "references")

