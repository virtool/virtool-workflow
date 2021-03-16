from virtool_workflow.analysis import fixtures as analysis_fixtures
from virtool_workflow.fixtures import FixtureGroup
from virtool_workflow.runtime.providers import providers

runtime = FixtureGroup(**providers)
"""A :class:`FixtureGroup` containing all fixtures available to the runtime."""

workflow = FixtureGroup(providers["job"])
"""A :class:`FixtureGroup` containing all fixtures available within workflows."""

analysis = FixtureGroup(**providers,
                        **{k: getattr(analysis_fixtures, k)
                           for k in analysis_fixtures.__all__})
"""A :class:`FixtureGroup` containing all fixtures excusive to analysis workflows."""
