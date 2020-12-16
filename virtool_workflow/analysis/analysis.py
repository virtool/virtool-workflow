from virtool_workflow import fixture
from virtool_workflow.abc.db import AbstractDatabase
from typing import Dict, Any


@fixture
async def analysis(job_args: Dict[str, Any], database: AbstractDatabase):
    document = await database.fetch_document_by_id(job_args["analysis_id"], "analyses")
    return document
