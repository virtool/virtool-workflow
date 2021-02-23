from virtool_workflow.fixtures.scoping import api_scope


@api_scope.fixture
def job_provider(job_id: str):
    ...
