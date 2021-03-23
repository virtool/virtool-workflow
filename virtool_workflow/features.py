from abc import ABC

from virtool_workflow import Workflow
from virtool_workflow.environment import WorkflowEnvironment
from virtool_workflow.fixtures.providers import FixtureProvider, FixtureGroup

_features = []


class WorkflowFeature(ABC):

    async def __modify_workflow__(self, workflow: Workflow) -> Workflow:
        """
        Called before the workflow is executed.

        The :class:`Workflow` returned by this method will be used in place of the original workflow.

        :param workflow: The workflow which is about to be executed.
        :return: The modified workflow.
        """
        ...

    @property
    def __fixtures__(self) -> FixtureProvider:
        """A :class:`FixtureProvider` which will be included in the workflow environment."""
        return FixtureGroup()

    async def __modify_environment__(self, environment: WorkflowEnvironment):
        """
        Called before the workflow is executed.

        :param environment: The :class:`WorkflowEnvironment` which will be used to execute the workflow.
        """
        ...


def install(*features: WorkflowFeature):
    """Install a workflow feature to be applied before the next workflow run."""
    _features.extend(features)


async def install_into_environment(environment: WorkflowEnvironment,
                                   *features: WorkflowFeature,
                                   workflow: Workflow = None):
    """
    Apply any installed workflow features to the workflow environment and workflow object.

    :param environment: The workflow environment.
    :param workflow: The workflow being executed.
    :param features: A list of features to apply. If None is given, the globally installed features will be used.
    """
    if not features:
        features = _features

    if workflow is None:
        workflow = environment["workflow"]

    for feature in features:
        await feature.__modify_workflow__(workflow)
        environment.add_provider(feature.__fixtures__)
        await feature.__modify_environment__(environment)

    if features is _features:
        features.clear()

    return environment
