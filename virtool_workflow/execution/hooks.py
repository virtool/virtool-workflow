import inspect
from typing import List, Any, Callable


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


def hook(func: Callable):
    params = _extract_params(func)
    func.callbacks = []

    is_coroutine = inspect.iscoroutinefunction(func)

    def _callback(callback: Callable):
        _validate_parameters(func, callback, params, _extract_params(callback))
        # noinspection PyUnresolvedReferences
        func.callbacks.append(callback)
        return callback

    func.callback = _callback
    return func


async def trigger_hook(hook, *args, **kwargs) -> List[Any]:
    return [await callback(*args, **kwargs) for callback in hook.callbacks]

