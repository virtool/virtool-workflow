"""Scoping and injection of workflow fixtures."""
import logging
import pprint
from contextlib import AbstractContextManager
from functools import wraps
from inspect import isgeneratorfunction, iscoroutinefunction, signature
from typing import Optional, Dict, Any, Type, Callable, Iterator, Union

from virtool_workflow.workflow import Workflow
from virtool_workflow.fixtures.workflow_fixture import WorkflowFixture
from virtool_workflow.fixtures.errors import WorkflowFixtureMultipleYield, WorkflowFixtureNotAvailable

logger = logging.getLogger(__name__)


class WorkflowFixtureScope(AbstractContextManager):
    """
    A scope maintaining instances of workflow fixtures.

    Fixture instances can be bound to functions using the #.bind() method.
    """

    def __init__(self,
                 instances: Optional[Dict[str, Any]] = None,
                 parent_scope: Optional["WorkflowFixtureScope"] = None):
        """

        :param instances: Any objects to be maintained as instance fixtures.
            Values in this dictionary will be accessible as fixtures by their key.
        :param parent_scope: Another WorkflowFixtureScope to inherit instances from.
            Note that exiting this WorkflowFixtureScope will not invoke __exit__ on the
            parent scope.
        """
        self._instances = {"scope": self}
        self._generators = []

        if instances:
            self._instances.update(instances)
        if parent_scope:
            self._instances.update(parent_scope._instances)

    def __enter__(self):
        """Return this instance when `with` statement is used."""
        logger.debug(f"Opening a new {WorkflowFixtureScope.__name__}")
        return self

    def __exit__(self, *args, **kwargs):
        """
        Remove references to any instances managed by this WorkflowFixtureScope.

        Return execution to each of the generator fixtures and remove
        references to them.
        """
        logger.debug(f"Closing {WorkflowFixtureScope.__name__} {self}")
        logger.debug("Clearing instances")
        self._instances = {}
        # return control to the generator fixtures which are still left open
        for gen in self._generators:
            logger.debug(f"Returning control to generator fixture {gen}")
            none = next(gen, None)
            if none is not None:
                raise WorkflowFixtureMultipleYield("Fixture must only yield once")
        logger.debug("Clearing generators")
        self._generators = []

    async def instantiate(self, fixture_: Union[WorkflowFixture, Type[WorkflowFixture]]) -> Any:
        """
        Create an instance of a fixture.

        The instance will be stored within this WorkflowFixtureScope.

        :param fixture_: The fixture class to instantiate
        :return: The instantiated fixture instance.

        """
        __fixture__ = getattr(fixture_.__class__, "__fixture__", None)
        if not __fixture__:
            __fixture__ = getattr(fixture_, "__fixture__")

        bound = await self.bind(__fixture__)

        if isgeneratorfunction(__fixture__):
            generator = bound()
            self._generators.append(generator)
            instance = next(generator)
        elif iscoroutinefunction(__fixture__):
            instance = await bound()
        else:
            instance = bound()

        self._instances[fixture_.param_name] = instance

        logger.debug(f"Instantiated {fixture_} as {instance}")

        return instance

    async def get_or_instantiate(self, name: str):
        """
        Get an instance of the workflow fixture with a given name. If there exists an
        instance cached in this WorkflowFixtureScope it will returned, else a new instance
        will be created and cached.

        :param name: The name of the workflow fixture to get
        :return: The workflow fixture instance for this WorkflowFixtureScope
        :raise KeyError: When the given name does not correspond to a defined workflow fixture.
        """
        if name in self._instances:
            return self._instances[name]

        fixture_types = WorkflowFixture.types()
        if name in fixture_types:
            return await self.instantiate(fixture_types[name])

        raise KeyError(name, f"{name} is not defined as a workflow fixture")

    def __getitem__(self, item: str):
        """Get a fixture instance if one is instantiated within this WorkflowFixtureScope."""
        try:
            return self._instances.__getitem__(item)
        except KeyError as error:
            raise ValueError(
                f"{error} is not available within this scope.\n"
                f"Available instances are: \n {pprint.pformat(self._instances)}"
            )

    def __setitem__(self, key: str, value: Any):
        """Add an instance as a fixture with this WorkflowFixtureScope."""
        return self._instances.__setitem__(key, value)

    def __delitem__(self, key: str):
        """Support `del` keyword."""
        return self._instances.__delitem__(key)

    def __contains__(self, item):
        """Support `in` operator."""
        return self._instances.__contains__(item)

    def add_instance(self, instance: Any, *names: str):
        """
        Add an instance as a fixture within this WorkflowFixtureScope only. The instance
        will be bound directly and no subclass of WorkflowFixture will be created.

        :param instance: The instance to use as a workflow fixture
        :param names: Any names the workflow fixture should be accessible by
                      (in function parameters)
        """
        for name in names:
            self.__setitem__(name, instance)

    async def bind(self, func: Callable[..., Any], strict: bool = True) -> Callable[[], Any]:
        """
        Bind fixtures to the parameters of a function.

        Positional arguments and non-fixture keyword arguments
        of the function will be preserved. Essentially,The fixtures & other keyword
        arguments given are added as keyword arguments to the function.

        :param func: The function requiring workflow fixtures to be bound
        :param strict: A flag indicating that all parameters must be bound to a fixture, defaults to True
        :return: A new function with it's arguments appropriately bound
        :raise WorkflowFixtureNotAvailable: When `func` requires an argument
            which cannot be bound due to no fixture of it's name being available.
        """
        sig = signature(func)

        fixtures = {}
        for param in sig.parameters:
            try:
                fixtures[param] = await self.get_or_instantiate(param)
            except KeyError as key_error:
                if strict:
                    missing_param = key_error.args[0]
                    raise WorkflowFixtureNotAvailable(param_name=missing_param, signature=sig, func=func)

        if iscoroutinefunction(func):
            @wraps(func)
            async def bound(*args, **_kwargs) -> Iterator[Any]:
                _kwargs.update(fixtures)
                return await func(*args, **_kwargs)
        else:
            @wraps(func)
            def bound(*args, **_kwargs) -> Any:
                _kwargs.update(fixtures)
                return func(*args, **_kwargs)

        return bound

    async def bind_to_workflow(self, workflow: Workflow):
        """
        Bind workflow fixtures to all functions for a given Workflow

        :param workflow: The Workflow requiring workflow fixtures
        :return: A new workflow with fixtures bound to all functions
        """
        bound_workflow = Workflow()
        bound_workflow.on_startup = [await self.bind(f) for f in workflow.on_startup]
        bound_workflow.on_cleanup = [await self.bind(f) for f in workflow.on_cleanup]
        bound_workflow.steps = [await self.bind(f) for f in workflow.steps]
        return bound_workflow
