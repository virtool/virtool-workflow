"""Scoping and injection of workflow fixtures."""
import inspect
import logging
import pprint
from contextlib import AbstractAsyncContextManager, suppress
from functools import wraps
from inspect import signature, Parameter
from typing import Any, Callable

from virtool_workflow.fixtures.errors import FixtureMultipleYield, FixtureNotAvailable
from virtool_workflow.fixtures.providers import FixtureProvider, InstanceFixtureGroup, FixtureGroup
from virtool_workflow.workflow import Workflow

logger = logging.getLogger(__name__)


class FixtureScope(AbstractAsyncContextManager, InstanceFixtureGroup):
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
        self._async_generators = []
        self.add_provider = self._providers.append
        self.add_providers = self._providers.extend

        super(FixtureScope, self).__init__()

    async def __aenter__(self):
        """Return this instance when `with` statement is used."""
        logger.debug(f"Opening a new {FixtureScope.__name__}")
        return self

    async def close(self):
        """
        Remove references to any instances managed by this WorkflowFixtureScope.

        Return execution to each of the generator fixtures and remove
        references to them.
        """
        logger.debug(f"Closing {FixtureScope.__name__} {self}")
        # return control to the generator fixtures which are still left open
        self.clear()

        while self._generators:
            gen = self._generators.pop()
            logger.debug(f"Returning control to generator fixture {gen}")
            none = next(gen, None)
            if none is not None:
                raise FixtureMultipleYield("Fixture must only yield once")

        while self._async_generators:
            gen = self._async_generators.pop()
            logger.debug(f"Returning control to async generator fixture {gen}")
            with suppress(StopAsyncIteration):
                await gen.__anext__()
                raise FixtureMultipleYield("Fixture must only yield once")

        for provider in self._providers:
            if isinstance(provider, FixtureScope) and id(provider) != id(self):
                await provider.close()

    async def __aexit__(self, *args, **kwargs):
        """Close the :class:`FixtureScope` on exit."""
        await self.close()

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

        instance = await bound()

        with suppress(TypeError):
            generator = instance
            instance = next(generator)
            self._generators.append(generator)

        with suppress(TypeError, AttributeError):
            async_generator = instance
            instance = await instance.__anext__()
            self._async_generators.append(async_generator)

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
        with suppress(KeyError):
            return self[name]

        try:
            fixture = self._get_fixture_from_providers(name, requested_by)
        except TypeError:
            raise KeyError(f"{name} is not a fixture within this FixtureScope.")

        return await self.instantiate(fixture)

    def __getitem__(self, item: str):
        """Get a fixture instance if one is instantiated within this WorkflowFixtureScope."""
        try:
            return super().__getitem__(item)
        except KeyError as error:
            raise KeyError(
                f"{error} is not available within this scope.\n"
                f"Available instances are: \n {pprint.pformat(dict(self))}"
            )

    async def bind(self, func, strict=False):
        return self.bound(func, strict)

    def bound(self, func: Callable[..., Any], strict: bool = False) -> Callable[[], Any]:
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

        async def _bind(func, fixtures):
            for name, parameter in sig.parameters.items():
                try:
                    fixtures[name] = await self.get_or_instantiate(name, requested_by=func)
                except KeyError as key_error:
                    if strict:
                        if parameter.default == Parameter.empty:
                            # Parameter does not have a default value.
                            raise FixtureNotAvailable(key_error.args[0], signature=sig, func=func, scope=self)
            return fixtures

        @wraps(func)
        async def _bound(*args, **_kwargs):
            fixtures = await _bind(func, {})
            fixtures.update(_kwargs)
            try:
                return await func(*args, **fixtures)
            except TypeError as e:
                if not inspect.iscoroutinefunction(func):
                    try:
                        return func(*args, **fixtures)
                    except TypeError as missing_params:
                        raise FixtureNotAvailable(missing_params.args[0], sig, func, self) from missing_params
                raise e

        return _bound

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
