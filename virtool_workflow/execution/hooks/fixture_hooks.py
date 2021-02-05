from inspect import signature
from typing import List, Any, Callable

from virtool_workflow import utils
from virtool_workflow.execution.hooks.hooks import Hook
from virtool_workflow.fixtures.scope import FixtureScope


class FixtureHook(Hook):
    """A Hook which binds fixtures to it's callback functions before invoking them."""

    def _callback(self, callback_: Callable):
        """Register a callback function, skipping parameter validation"""
        callback_ = utils.coerce_to_coroutine_function(callback_)
        self.callbacks.append(callback_)
        return callback_

    async def trigger(self, scope: FixtureScope, *args, **kwargs) -> List[Any]:
        """Bind fixtures from `scope` to each callback function and invoke them."""
        scope["scope"] = scope
        print(self.name)

        print(self.callbacks)
        _callbacks = [await scope.bind(callback, strict=not bool(args)) for callback in self.callbacks]
        print("""waaa""")
        _callbacks = [utils.coerce_coroutine_function_to_accept_any_parameters(callback)
                      if len(signature(callback).parameters) == 0 else callback
                      for callback in _callbacks]
        print("ADWD")

        return [await callback(*args, **kwargs) for callback in _callbacks]
