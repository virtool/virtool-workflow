"""Scoping and injection of workflow fixtures."""
from contextlib import AbstractContextManager

import logging
import pprint
from collections.abc import MutableMapping
from functools import wraps
from inspect import isgeneratorfunction, iscoroutinefunction, signature
from typing import Any, Callable, Iterator

from virtool_workflow.fixtures.errors import FixtureMultipleYield, FixtureNotAvailable
from virtool_workflow.fixtures.providers import FixtureProvider, DictProvider, workflow_fixtures, workflow_fixtures_dict
from virtool_workflow.workflow import Workflow

logger = logging.getLogger(__name__)


class WorkflowFixtureScope(AbstractContextManager, MutableMapping):
    """
    A scope maintaining instances of workflow fixtures.

    Fixture instances can be bound to functions using the :func:`.bind()` method.
    """

    def __init__(self, *providers: FixtureProvider, **instances):
        """
        :param providers: :class:`FixtureProvider` functions for accessing fixtures. Providers will be checked
            in the order they are given. The `virtool_workflow.fixtures.providers.workflow_fixture` provider is
            already included.

        :param instances: Any objects to be maintained as instance fixtures.
            Values in this dictionary will be accessible as fixtures by their key. Also note that these
            fixtures will take precedence over those provided by the elements of :obj:`providers`.
        """
        self._instances = DictProvider(scope=self, **instances)
        self._providers = [self._instances, workflow_fixtures, *providers]
        self._generators = []

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
        # return control to the generator fixtures which are still left open
        self._instances.clear()
        for gen in self._generators:
            logger.debug(f"Returning control to generator fixture {gen}")
            none = next(gen, None)
            if none is not None:
                raise FixtureMultipleYield("Fixture must only yield once")
        logger.debug("Clearing generators")
        self._generators = []

    @property
    def available(self):
        return {**self._instances, **workflow_fixtures_dict}

    async def instantiate(self, fixture_: Callable) -> Any:
        """
        Create an instance of a fixture.

        The instance will be stored within this WorkflowFixtureScope.

        :param fixture_: The fixture class to instantiate
        :return: The instantiated fixture instance.

        """

        bound = await self.bind(fixture_)

        if isgeneratorfunction(fixture_):
            generator = bound()
            self._generators.append(generator)
            instance = next(generator)
        elif iscoroutinefunction(fixture_):
            instance = await bound()
        else:
            instance = bound()

        self._instances[fixture_.__name__] = instance

        logger.debug(f"Instantiated {fixture_} as {instance}")

        return instance

    def _get_fixture_from_providers(self, name, request_from: Callable = None):
        """Get the fixture function with the given name from this :class:`WorkflowFixtureScope`'s providers"""
        for provider in self._providers:
            fixture = provider(name, request_from)
            if fixture:
                return fixture

    async def get_or_instantiate(self, name: str, requested_by: Callable = None):
        """
        Get an instance of the workflow fixture with a given name. If there exists an
        instance cached in this WorkflowFixtureScope it will returned, else a new instance
        will be created and cached.

        :param name: The name of the workflow fixture to get
        :param requested_by: The callable for which the fixture is being fetched. Some :class:`FixtureProviders`
            will only provide fixtures for specific Callables.
        :return: The workflow fixture instance for this WorkflowFixtureScope
        :raise KeyError: When the given name does not correspond to a defined workflow fixture.
        """
        if name in self._instances:
            return self._instances[name]

        fixture = self._get_fixture_from_providers(name, requested_by)
        if fixture:
            return await self.instantiate(fixture)

        raise KeyError(name, f"{name} is not a fixture within this WorkflowFixtureScope.")

    def __iter__(self):
        return iter(self._instances)

    def __len__(self) -> int:
        return len(self._instances)

    def __getitem__(self, item: str):
        """Get a fixture instance if one is instantiated within this WorkflowFixtureScope."""
        try:
            return self._instances[item]
        except KeyError as error:
            raise ValueError(
                f"{error} is not available within this scope.\n"
                f"Available instances are: \n {pprint.pformat(self._instances)}"
            )

    def __setitem__(self, key: str, value: Any):
        """Add an instance as a fixture with this WorkflowFixtureScope."""
        self._instances[key] = value

    def __delitem__(self, key: str):
        """Support `del` keyword."""
        del self._instances[key]

    def __contains__(self, item):
        """Support `in` operator."""
        return item in self._instances

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
                fixtures[param] = await self.get_or_instantiate(param, requested_by=func)
            except KeyError as key_error:
                if strict:
                    missing_param = key_error.args[0]
                    raise FixtureNotAvailable(param_name=missing_param, signature=sig, func=func, scope=self)

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
