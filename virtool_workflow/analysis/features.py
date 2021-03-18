from abc import abstractmethod, ABC

from virtool_workflow import Workflow
from virtool_workflow.environment import WorkflowEnvironment
from virtool_workflow.fixtures.providers import FixtureProvider

_features = []


class WorkflowFeature(ABC):

    @abstractmethod
    async def __modify_workflow__(self, workflow: Workflow) -> Workflow:
        ...

    @property
    @abstractmethod
    def __fixtures__(self) -> FixtureProvider:
        ...

    @abstractmethod
    async def __modify_environment__(self, environment: WorkflowEnvironment) -> WorkflowEnvironment:
        ...


def install(*features: WorkflowFeature):
    """"""
    _features.extend(features)


async def install_into_environment(environment: WorkflowEnvironment, features=None):
    if not features:
        features = _features

    for feature in features:
        environment["workflow"] = await feature.__modify_workflow__(environment["workflow"])
        environment.add_provider(feature.__fixtures__)
        environment = await feature.__modify_environment__(environment)
