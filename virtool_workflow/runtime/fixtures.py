from virtool_workflow.fixtures import FixtureGroup

runtime = FixtureGroup()
"""A :class:`FixtureGroup` containing all fixtures available to the runtime."""
workflow = FixtureGroup()
"""A :class:`FixtureGroup` containing all fixtures available within workflows."""
analysis = FixtureGroup()
"""A :class:`FixtureGroup` containing all fixtures excusive to analysis workflows."""
