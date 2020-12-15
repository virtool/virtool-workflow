from virtool_workflow import fixture
from virtool_workflow.db import db
from typing import Dict, Any


@fixture
async def analysis(job_args: Dict[str, Any]):
    document = await db.fetch_document_by_id(job_args["analysis_id"], "analyses")
    return document
