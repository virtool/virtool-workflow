import inspect
import functools
from typing import List, Any, Callable, Coroutine
from abc import ABC, abstractmethod


class IncompatibleCallback(ValueError):
    pass


class ParameterMismatch(IncompatibleCallback):
    pass


class TypeHintMismatch(ParameterMismatch):
    pass


def _extract_params(func: Callable):
    parameters = inspect.signature(func).parameters
    return list(parameters.values())


def _validate_parameters(
        hook: Callable,
        callback: Callable,
        hook_params: List[inspect.Parameter],
        callback_params: List[inspect.Parameter]
):
    if len(callback_params) != len(hook_params):
        raise ParameterMismatch(f"{callback} takes {len(callback_params)} parameters "
                                f"where {hook} takes {len(hook_params)} parameters.")
    for hook_param, callback_param in zip(hook_params, callback_params):
        if hook_param.annotation is inspect.Parameter.empty:
            continue
        if callback_param.annotation is inspect.Parameter.empty:
            continue
        if hook_param.annotation != callback_param.annotation:
            raise TypeHintMismatch(f"({callback_param}) of {callback} does not "
                                   f"match the type of ({hook_param}) of {hook}.")


def _validate_coroutine_sync_vs_async(
        hook: Callable,
        callback: Callable,
        hook_is_coroutine: bool,
        callback_is_coroutine: bool
):
    if hook_is_coroutine != callback_is_coroutine:
        if hook_is_coroutine:
            raise IncompatibleCallback(f"{callback} is not an async function, but"
                                       f"{hook} callbacks are asynchronous")
        else:
            raise IncompatibleCallback(f"{callback} is an async function, but {hook} callbacks "
                                       f"are synchronous")


async def _trigger_async_hook(hook_, *args, **kwargs) -> List[Any]:
    return [await callback(*args, **kwargs) for callback in hook_.callbacks]


class AbstractHook(ABC):

    @abstractmethod
    def callback(self, callback_: Callable) -> Callable:
        pass

    @abstractmethod
    def __trigger__(self, *args, **kwargs) -> List[Any]:
        pass


class Hook(AbstractHook):

    def __init__(self, function):
        self._function = function
        self._params = _extract_params(function)
        self.callbacks = []

    def callback(self, callback_: Callable):
        _validate_parameters(self._function, callback_, self._params, _extract_params(callback_))
        self.callbacks.append(callback_)
        return callback_

    def __call__(self, *args, **kwargs):
        self._function(*args, **kwargs)

    def __trigger__(self, *args, **kwargs) -> List[Any]:
        return [callback(*args, **kwargs) for callback in self.callbacks]

class AsyncHook(Hook):

    def callback(self, callback_: Callable[..., Coroutine[Any, Any, Any]]):
        return super().callback(callback_)

    async def __call__(self, *args, **kwargs):
        return await self._function(*args, **kwargs)



def hook(func: Callable):
    params = _extract_params(func)
    func.callbacks = []

    is_coroutine = inspect.iscoroutinefunction(func)

    def _callback(callback: Callable):

    func.callback = _callback

    if is_coroutine:
        func.__trigger__ = functools.partial(_trigger_async_hook, func)
    else:
        func.__trigger__ = functools.partial(_trigger_sync_hook, func)

    return func


def trigger_hook(hook_: Callable, *args, **kwargs) -> List[Any]:
    return hook_.__trigger__(*args, **kwargs)