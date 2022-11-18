from asyncio import gather
from logging import getLogger
from typing import Any, Callable, List

from pyfixtures import FixtureScope

from virtool_workflow.runtime.utils import coerce_to_coroutine_function

logger = getLogger("hooks")


class Hook:
    """Used to hook into the workflow lifecycle."""

    def __init__(self, hook_name: str):
        """
        A set of functions to be called as a group upon a particular event.

        The signature of any functions added via :func:`Hook.callback` or
        :func:`Hook.__call__` are validated to match the types provided.

        :param hook_name: The name of this hook.
        """
        self.name = hook_name

        self.callbacks = []

        self.clear = self.callbacks.clear

    def __call__(self, callback_: Callable = None, until=None, once=False):
        """
        Add a callback function to this Hook that will be called when the hook is
        triggered.

        :param callback_: The callback function to register.
        :param until: Don't call the callback after the passed hook has been triggered.
        :param once: Only execute the callback the next time this hook is triggered.
        :return: The passed callback function as a coroutine.
        """
        if once:
            until = self
        if callback_ and not until:
            cb = self._callback(callback_)
        elif callback_ and until:
            cb = self._callback_until(until)(callback_)
        elif until:
            cb = self._callback_until(until)
        else:
            cb = self._callback

        if callback_ is not None:
            logger.debug(
                f"Registered callback {callback_.__name__}() onto hook {self.name}"
            )
        return cb

    def _callback(self, callback_: Callable):
        """Register a callback function, skipping parameter validation"""
        callback_ = coerce_to_coroutine_function(callback_)
        self.callbacks.append(callback_)
        return callback_

    def _callback_until(self, hook_: "Hook"):
        """Add a callback to this hook and remove it when :func:`hook_` is triggered."""

        def _temporary_callback(callback_):
            callback_ = self._callback(callback_)

            @hook_._callback
            def remove_callback():
                self.callbacks.remove(callback_)
                hook_.callbacks.remove(remove_callback)

            return callback_

        return _temporary_callback

    async def trigger(self, scope: FixtureScope, suppress=False, **kwargs) -> List[Any]:
        """
        Trigger the hook.

        Bind fixtures from `scope` to each callback function and invoke them.

        Each callback function registered by :func:`Hook.callback` or
        :func:`Hook.__call__` will be called using the arguments supplied to this
        function.

        :param scope: the :class:`FixtureScope` to use to bind fixtures
        :param suppress: suppress and log exceptions raised in callbacks
        """
        logger.debug(f"Triggering {self.name} hook with callbacks: {self.callbacks}")

        if "scope" not in scope:
            scope["scope"] = scope

        async def _bind(callback_: Callable):
            logger.debug(f"Binding fixtures to callback {callback_}")
            try:
                return await scope.bind(callback_, **kwargs)
            except KeyError as error:
                if suppress:
                    logger.exception(error)
                    return lambda: None

                raise error

        _callbacks = [await _bind(callback) for callback in self.callbacks]

        return await self._trigger(_callbacks, suppress_errors=suppress)

    @staticmethod
    async def _trigger(callbacks, *args, suppress_errors=False, **kwargs):
        async def call_callback(callback):
            logger.debug(f"Calling {callback}.")
            if suppress_errors:
                try:
                    return await callback(*args, **kwargs)
                except Exception as error:
                    logger.exception(error)
            else:
                return await callback(*args, **kwargs)

        results = await gather(
            *[call_callback(callback) for callback in callbacks], return_exceptions=True
        )

        for error in results:
            if isinstance(error, Exception):
                raise error

        return results
