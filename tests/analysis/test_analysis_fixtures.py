import virtool_workflow.workflow_fixture
from virtool_workflow.analysis.analysis_jobs import analysis
from virtool_workflow.workflow_fixture import WorkflowFixtureScope
from virtool_workflow.analysis.library_types import LibraryTypes


TEST_ANALYSIS_INFO = (
        "1",
        "1",
        "1",
        "1",
        dict(
            _id="1",
            paired=True,
            library_type=LibraryTypes.amplicon,
            quality=dict(
                length=["", "1"],
                count="3"
            )
        ),
        dict(
            subtraction=dict(id="id with spaces")
        )
    )


async def test_analysis_fixture_instantiation():
    with WorkflowFixtureScope() as scope:
        scope["job_id"] = "1"

        scope["analysis_info"] = TEST_ANALYSIS_INFO

        await scope.get_or_instantiate("analysis")

        assert scope["analysis"]
        # TODO: write more comprehensive checks


async def test_real_analysis_info_fixture_is_used():
    with WorkflowFixtureScope() as scope:
        scope["job_id"] = "1"

        await scope.get_or_instantiate("analysis")
        pass