from typing import List, Any, Type, Optional, Callable
from inspect import signature

from virtool_workflow import utils
from virtool_workflow.execution.hooks import Hook
from virtool_workflow.fixtures.scope import WorkflowFixtureScope


class HookRequirementNotProvided(Exception):
    def __init__(self, hook: Hook, name: str, type: Optional[Type]):
        super().__init__(f"The {hook.name} hook's `.trigger` method requires keyword argument {name}: {type}")


class WorkflowFixtureHook(Hook):
    """A Hook which binds fixtures to it's callback functions before invoking them."""

    def _callback(self, callback_: Callable):
        """Register a callback function, skipping parameter validation"""
        callback_ = utils.coerce_to_coroutine_function(callback_)
        self.callbacks.append(callback_)
        return callback_

    async def trigger(self, scope: WorkflowFixtureScope, *args, **kwargs) -> List[Any]:
        """Bind fixtures from `scope` to each callback function and invoke them."""
        scope["scope"] = scope

        _callbacks = [await scope.bind(callback, strict=False) for callback in self.callbacks]
        _callbacks = [utils.coerce_coroutine_function_to_accept_any_parameters(callback)
                      if len(signature(callback).parameters) == 0 else callback
                      for callback in _callbacks]

        return [await callback(*args, **kwargs) for callback in _callbacks]

