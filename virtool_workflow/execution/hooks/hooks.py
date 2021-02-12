"""Create hooks for triggering and responding to events."""
import logging
import pprint
from typing import List, Any, Callable

from virtool_workflow.utils import coerce_to_coroutine_function

logger = logging.getLogger(__name__)


class Hook:

    def __init__(self, hook_name, parameters, return_type):
        """
        A set of functions to be called as a group upon a particular event.

        The signature of any functions added (via :func:`Hook.callback` or :func:`Hook.__call__`)
        are validated to match the types provided.

        :param hook_name: The name of this hook.
        :param parameters: A list of types for the parameters a callback function
            should accept. These will be used to validate function signatures before
            adding them to the set.

        :param return_type: The expected return type for callback functions.
        """
        self.name = hook_name
        self._params = parameters
        self._return = return_type

        self.callbacks = []

        self.clear = self.callbacks.clear

    def callback(self, callback_: Callable = None, until=None, once=False):
        """
        Add a callback function to this Hook, to be invoked on :func:`.trigger()`

        :param callback_: The callback function to register.

        :param until: Another :class:`Hook` which signals that the registered callback
            function should no longer be called by this hook. When the other hook is
            triggered, the callback function `callback_` will be removed from the set of callbacks.

        :param once: Only execute the callback the next time this Hook is triggered.
        :return: The original value of `callback_` if it was a coroutine function, else a coroutine
            wrapping :func:`callback_`.
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

        logger.debug(f"Registered callback {callback_} onto hook {self.name}")
        return cb

    __call__ = callback

    def _callback(self, callback_: Callable) -> Callable:
        """Validate and add a callback to this Hook."""
        callback_ = coerce_to_coroutine_function(callback_)
        self.callbacks.append(callback_)
        return callback_

    def _callback_until(self, hook_: "Hook"):
        """Add a callback to this hook and have it removed once :func:`hook_` is triggered. """

        def _temporary_callback(callback_):
            callback_ = self._callback(callback_)

            @hook_._callback
            def remove_callback():
                self.callbacks.remove(callback_)
                hook_.callbacks.remove(remove_callback)

            return callback_

        return _temporary_callback

    async def trigger(self, *args, **kwargs) -> List[Any]:
        """
        Trigger this Hook.

        Each callback function registered by :func:`Hook.callback` or :func:`Hook.__call__`
        will be called using the arguments supplied to this function.

        :param args: Positional Arguments for this Hook.
        :param kwargs: Keyword arguments for this Hook.
        :return List[Any]: The results of each callback function.
        """
        logger.debug(f"Triggering {self.name} hook with callback functions: {pprint.pformat(self.callbacks)}")
        return [await callback(*args, **kwargs) for callback in self.callbacks]
