"""Scoping and injection of workflow fixtures."""
from contextlib import AbstractContextManager

import logging
import pprint
from functools import wraps
from inspect import iscoroutinefunction, signature
from types import GeneratorType
from typing import Any, Callable, Iterator

from virtool_workflow.fixtures.errors import FixtureMultipleYield, FixtureNotAvailable
from virtool_workflow.fixtures.providers import FixtureProvider, InstanceFixtureGroup, FixtureGroup
from virtool_workflow.workflow import Workflow

logger = logging.getLogger(__name__)


class FixtureScope(AbstractContextManager, InstanceFixtureGroup):
    """
    A scope maintaining instances of workflow fixtures.

    Fixture instances can be bound to functions using the :func:`.bind()` method.
    """

    def __init__(self, *providers: FixtureProvider, **instances):
        """
        :param providers: :class:`FixtureProvider` functions for accessing fixtures. Providers will be checked
            in the order they are given. The `virtool_workflow.fixtures.data_providers.workflow_fixture` provider is
            already included.

        :param instances: Any objects to be maintained as instance fixtures.
            Values in this dictionary will be accessible as fixtures by their key. Also note that these
            fixtures will take precedence over those provided by the elements of :obj:`data_providers`.
        """
        self.update(**instances)
        self["scope"] = self
        self._overrides = FixtureGroup()
        self._providers = [self, self._overrides, *providers]
        self._generators = []
        self.add_provider = self._providers.append
        self.add_providers = self._providers.extend

        super(FixtureScope, self).__init__()

    def __enter__(self):
        """Return this instance when `with` statement is used."""
        logger.debug(f"Opening a new {FixtureScope.__name__}")
        return self

    def close(self):
        """
        Remove references to any instances managed by this WorkflowFixtureScope.

        Return execution to each of the generator fixtures and remove
        references to them.
        """
        logger.debug(f"Closing {FixtureScope.__name__} {self}")
        logger.debug("Clearing instances")
        # return control to the generator fixtures which are still left open
        self.clear()
        for gen in self._generators:
            logger.debug(f"Returning control to generator fixture {gen}")
            none = next(gen, None)
            if none is not None:
                raise FixtureMultipleYield("Fixture must only yield once")
        logger.debug("Clearing generators")
        self._generators = []

        for provider in self._providers:
            if isinstance(provider, FixtureScope) and id(provider) != id(self):
                provider.close()

    def __exit__(self, *args, **kwargs):
        """Close the :class:`FixtureScope` on exit."""
        self.close()

    @property
    def available(self):
        _available = {**self.fixtures()}
        for provider in self._providers:
            if isinstance(provider, FixtureGroup):
                _available.update(**provider.fixtures())
            elif isinstance(provider, InstanceFixtureGroup):
                _available.update(**provider)
        return _available

    async def instantiate(self, fixture_: Callable) -> Any:
        """
        Create an instance of a fixture.

        The instance will be stored within this WorkflowFixtureScope.

        :param fixture_: The fixture class to instantiate
        :return: The instantiated fixture instance.

        """

        bound = await self.bind(fixture_)

        if iscoroutinefunction(fixture_):
            instance = await bound()
        else:
            instance = bound()

        if isinstance(instance, GeneratorType):
            generator = bound()
            self._generators.append(generator)
            instance = next(generator)

        self[fixture_.__name__] = instance

        logger.debug(f"Instantiated {fixture_} as {instance}")

        return instance

    def _get_fixture_from_providers(self, name, request_from: Callable = None):
        """Get the fixture function with the given name from this :class:`WorkflowFixtureScope`'s data_providers"""
        for provider in self._providers:
            fixture = provider(name, request_from)
            if fixture is not None:
                return fixture

    async def get_or_instantiate(self, name: str, requested_by: Callable = None):
        """
        Get an instance of the fixture with a given name. If there exists an
        instance cached in this :class:`FixtureScope` it will be returned, else a new instance
        will be created and cached.

        :param name: The name of the workflow fixture to get
        :param requested_by: The callable from which the fixture is being fetched.
        :return: The workflow fixture instance for this :class:`FixtureScope`
        :raise KeyError: When the given name does not correspond to a defined workflow fixture.
        """
        if name in self:
            return self[name]

        fixture = self._get_fixture_from_providers(name, requested_by)
        if fixture:
            return await self.instantiate(fixture)

        raise KeyError(name, f"{name} is not a fixture within this WorkflowFixtureScope.")

    def __getitem__(self, item: str):
        """Get a fixture instance if one is instantiated within this WorkflowFixtureScope."""
        try:
            return super().__getitem__(item)
        except KeyError as error:
            raise ValueError(
                f"{error} is not available within this scope.\n"
                f"Available instances are: \n {pprint.pformat(dict(self))}"
            )

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

    def override(self, name: str, callable_: Callable):
        """
        Override a fixture within this scope.

        :param name: The name of the fixture to override
        :param callable_: A :class:`Callable` to use as the fixture
        """
        if name in self:
            del self[name]
        self._overrides[name] = callable_
