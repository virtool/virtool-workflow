import logging
import pprint
from fixtures import FixtureScope
from typing import List, Any, Callable

from virtool_workflow import utils
from virtool_workflow.execution.hooks.hooks import Hook

logger = logging.getLogger(__name__)


class FixtureHook(Hook):
    """A Hook which binds fixtures to it's callback functions before invoking them."""

    def _callback(self, callback_: Callable):
        """Register a callback function, skipping parameter validation"""
        logger.debug(f"Registered callback {callback_} onto hook {self.name}")
        callback_ = utils.coerce_to_coroutine_function(callback_)
        self.callbacks.append(callback_)
        return callback_

    async def trigger(self, scope: FixtureScope, suppress=False, **kwargs) -> List[Any]:
        """
        Bind fixtures from `scope` to each callback function and invoke them.

        :param scope: The :class:`FixtureScope` to use to bind fixtures.
        :param args: Any positional arguments to pass to the callback functions, after fixtures have been bound.
        :param suppress: If true, errors raised within the callback functions will be suppressed and logged.
        """
        logger.debug(
            f"Triggering {self.name} hook with callback functions: \n{pprint.pformat(self.callbacks, indent=4)}")
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
                else:
                    raise error

        _callbacks = [await _bind(callback) for callback in self.callbacks]

        return await self._trigger(_callbacks, suppress_errors=suppress)
