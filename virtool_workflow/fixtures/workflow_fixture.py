"""Pytest-style fixtures for use in Virtool Workflows."""
from abc import abstractmethod, ABC
from typing import Callable, Optional, List, Type


class WorkflowFixture(ABC):
    """
    Abstract base class for all workflow fixtures. This class is used primarily to keep
    track of all available fixtures via :func:`WorkflowFixture.__subclasses__`.

    The :func:`workflow_fixture` decorator function creates a new subclass of WorkflowFixture with
    the same name as the function passed to :func:`workflow_fixture`. The decorator
    returns an instance of the newly created class, which is callable with the same
    parameters as the function passed to the decorator.
    """
    param_names: List[str]

    def __init_subclass__(cls, param_names: List[str] = None, param_name: str = None, **kwargs):
        """
        Used to set the parameter names by which this fixture will be accessible
        within a workflow function.

        :param param_names: A list of names for this fixture to be injected for
        :param param_name: A name for this fixture to be injected for
        """
        if not param_names:
            if param_name:
                param_names = [param_name]
            else:
                raise ValueError("Must provide `param_names` or `param_name` argument to subclass")

        cls.param_names = param_names

    @staticmethod
    @abstractmethod
    def __fixture__(*args, **kwargs) -> Type["WorkflowFixture"]:
        """A function producing an instance to be used as a workflow fixture."""

    def __call__(self):
        return self.__fixture__()

    @staticmethod
    def types():
        """
        Get all currently available types of workflow fixtures.

        @return: A dict mapping workflow fixture names to
                 their respective :class:`WorkflowFixture` subclasses
        """
        return {name: cls for cls in WorkflowFixture.__subclasses__() for name in cls.param_names}


def fixture(func: Callable, name: Optional[str] = None):
    """
    Define a new :class:`WorkflowFixture`.

    A subclass of :class:`WorkflowFixture` is created with the same name as the
    provided function. An instance of the new subclass which is callable with the same
    parameters as the original function is then returned. This allows the fixture
    to be discovered automatically via :func:`.__subclasses__`.

    Workflow fixtures can be either async or standard functions. They can also be
    generator functions which only yield a single value. Any code after the yield statement
    will be executed when the :class:`WorkflowFixtureScope` closes.

    Workflow fixtures may accept other fixtures as parameters. They will be discovered as long
    as they have been imported (and are accessible by WorkflowFixture.__subclasses__).

    :param func: A function returning some value to be used as a workflow fixture
    :param name: A name for the created fixture, by default the name of `func` is used
    :return: An instance of a WorkflowFixture subclass that acts like the original function.
    """
    class _Fixture(WorkflowFixture, param_names=[func.__name__]):
        __fixture__ = func

    _Fixture.__name__ = _Fixture.__qualname__ = name if name else func.__name__
    return _Fixture()
