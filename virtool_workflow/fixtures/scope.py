"""Scoping and injection of workflow fixtures."""
import inspect
import asyncio
import logging
from contextlib import AbstractAsyncContextManager, suppress
from functools import wraps
from inspect import signature
from typing import Any, Callable
from virtool_workflow.utils import coerce_to_coroutine_function, wrapped_partial

from virtool_workflow.fixtures.errors import (
    FixtureNotFound,
    FixtureBindingError,
    FixtureMultipleYield
)
from virtool_workflow.fixtures.providers import (
    FixtureGroup,
    FixtureProvider,
    InstanceFixtureGroup,
)
from virtool_workflow.workflow import Workflow

logger = logging.getLogger(__name__)


class FixtureScope(AbstractAsyncContextManager, InstanceFixtureGroup):
    """A scope maintaining instances of fixtures."""

    def __init__(self,
                 *providers: FixtureProvider,
                 scope_name: str = None,
                 **instances):
        """
        :param providers: :class:`FixtureProvider` functions for accessing
            fixtures. Providers will be checked in the order they are given.

        :param scope_name: A name to use for this scope in logging messages.
        :param instances: Any objects to be maintained as instance fixtures.
        """
        self.update(**instances, scope=self)
        self._overrides = FixtureGroup()
        self._providers = [self, self._overrides, *providers]
        self._generators, self._async_generators = [], []

        self.add_provider = self._providers.append
        self.add_providers = self._providers.extend

        self.name = scope_name or id(self)
        self.open = False
        self.closed = False

        super(FixtureScope, self).__init__()

    async def __aenter__(self):
        """Return this instance when `with` statement is used."""
        logger.info(f"Opening {FixtureScope.__name__} {self.name}")
        self.open = True
        return self

    async def close(self):
        """
        Close the :class:`FixtureScope`.

        - Remove references to any instances
        - Return control to each generator fixture
        - Return control to each async generator fixture
        - Remove references to generators and async generators
        """
        logger.info(f"Closing {FixtureScope.__name__} {self.name}")

        self.clear()

        async def return_control_to_generator(gen):
            with suppress(StopIteration):
                logger.debug(f"Returning control to {gen}")
                next(gen)
                raise FixtureMultipleYield("Fixture must only yield once")

        async def return_control_to_async_generator(gen):
            with suppress(StopAsyncIteration):
                logger.debug(f"Returning control to {gen}")
                await gen.__anext__()
                raise FixtureMultipleYield("Fixture must only yield once")

        tasks = [return_control_to_generator(gen)
                 for gen in self._generators]

        tasks.extend([
            return_control_to_async_generator(gen)
            for gen in self._async_generators
        ])

        self._generators.clear()
        self._async_generators.clear()

        tasks.extend([
            provider.close() for provider in self._providers
            if id(provider) != id(self) and hasattr(provider, "close")
        ])

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for error in results:
            if isinstance(error, Exception):
                raise error

        self.closed = True

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

        if inspect.isgenerator(instance):
            self._generators.append(instance)
            instance = next(instance)

        elif inspect.isasyncgen(instance):
            self._async_generators.append(instance)
            instance = await instance.__anext__()

        self[fixture_.__name__] = instance

        logger.debug(f"Instantiated {fixture_} as {instance}")
        return instance

    def _get_fixture_from_providers(self, name, request_from: Callable = None):
        """
        Search all providers for a fixture.

        :param name: The name of the fixture
        :request_from: The function which the fixture will be bound to
        :raise KeyError: When the fixture cannot be found
        """
        for provider in self._providers:
            fixture = provider(name, request_from)
            if fixture is not None:
                return fixture
        raise FixtureNotFound(name, self)

    async def get_or_instantiate(
        self, name: str, requested_by: Callable = None
    ):
        """
        Get the value of a fixture, instantiating the fixture if needed.

        :param name: The name of the workflow fixture to get
        :param requested_by: The function which teh fixture will be bound to
        :return: The value of the fixture
        :raise FixtureNotFound: When the fixture cannot be found
        """
        with suppress(KeyError):
            return self[name]

        fixture = self._get_fixture_from_providers(name, requested_by)
        return await self.instantiate(fixture)

    async def bind(self, func, **kwargs):
        """
        Bind fixture values to the parameters of a function.

        Fixtures are instantiated at the time that this function is called.

        :raise FixtureNotFound: When there is a parameter which does not
                                correspond to a fixture.
        """
        sig = signature(func)
        func = coerce_to_coroutine_function(func)

        kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

        fixtures = {}
        for name in sig.parameters:
            if name in kwargs:
                continue
            try:
                fixtures[name] = await self.get_or_instantiate(name, func)
            except Exception as error:
                raise FixtureBindingError(func, name) from error

        self.update(fixtures)
        kwargs.update(fixtures)

        return wrapped_partial(func, **kwargs)

    async def partial(self, func, *args, **kwargs):
        """
        Bind fixtures to the function using :func:`functools.partial`.
        """
        sig = signature(func)

        fixtures = {}
        for name in sig.parameters:
            try:
                fixtures[name] = await self.get_or_instantiate(name, func)
            except FixtureNotFound:
                pass

        self.update(fixtures)

        kwargs.update(fixtures)
        return wrapped_partial(func, *args, **kwargs)

    def bound(self, func: Callable[..., Any]) -> Callable[[], Any]:
        """
        Bind fixtures to the parameters of a function.

        Fixtures are instantiated when the bound function is called.

        :param func: The function requiring workflow fixtures to be bound
        :return: A new function which does not require arguments
        :raise KeyError: When a fixture cannot be found
        """
        sig = signature(func)
        func = coerce_to_coroutine_function(func)

        async def get_values(func, fixtures):
            for name, parameter in sig.parameters.items():
                fixtures[name] = await self.get_or_instantiate(
                    name, requested_by=func
                )

                return fixtures

        @wraps(func)
        async def _bound():
            fixtures = await get_values(func, {})
            return await func(**fixtures)

        return _bound

    async def bind_to_workflow(self, workflow: Workflow):
        """
        Bind workflow fixtures to all functions for a given Workflow

        :param workflow: The Workflow requiring workflow fixtures
        :return: A new workflow with fixtures bound to all functions
        """
        bound_workflow = Workflow()
        bound_workflow.on_startup = [
            await self.bind(f) for f in workflow.on_startup
        ]
        bound_workflow.on_cleanup = [
            await self.bind(f) for f in workflow.on_cleanup
        ]
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

    def fixture(self, fixture_: callable):
        return self.override(fixture_.__name__, fixture_)
