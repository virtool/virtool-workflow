import inspect
from typing import List, Any, Callable

from virtool_workflow import utils


class IncompatibleCallback(ValueError):
    """Raised when a callback function is not compatible with a Hook"""
    pass


class ParameterMismatch(IncompatibleCallback):
    """Raised when the parameters of a callback function are not compatible with a Hook."""
    pass


class TypeHintMismatch(ParameterMismatch):
    """
    Raised when the type hints of a positional parameter
    do not match between a callback function and a hook definition.
    """
    pass


def _extract_params(func: Callable, extract_return: bool = False):
    """Extract parameters from the signature of a function."""
    signature = inspect.signature(func)
    parameters = signature.parameters
    if extract_return:
        return list(parameters.values()), signature.return_annotation
    return list(parameters.values())


def _validate_parameters(
        hook_name: str,
        callback: Callable,
        hook_params: List[inspect.Parameter],
        callback_params: List[inspect.Parameter]
):
    """
    Validate the signature of a callback function against the hook expected parameter types.

    :param hook_name: The name of the hook, used in the exception message.
    :param callback: The callback function to be validated.
    :param hook_params: The parameter types to expect for the callback.
            only the type hints
    :param callback_params: The actual parameter types of the callback function.
    """
    if len(callback_params) == 0 and len(hook_params) != 0:
        callback = utils.coerce_to_coroutine_function(callback)
        return utils.coerce_coroutine_function_to_accept_any_parameters(callback)

    if len(callback_params) != len(hook_params):
        if all(callback_param.kind != inspect.Parameter.VAR_POSITIONAL for callback_param in callback_params):
            raise ParameterMismatch(f"{callback} takes {len(callback_params)} parameters "
                                    f"where {hook_name} takes {len(hook_params)} parameters.")

    for hook_param, callback_param in zip(hook_params, callback_params):
        if hook_param.annotation is inspect.Parameter.empty or \
                callback_param.annotation is inspect.Parameter.empty:
            continue

        if hook_param.annotation != callback_param.annotation:
            raise TypeHintMismatch(f"({callback_param}) of {callback} does not "
                                   f"match the type of ({hook_param}) of {hook_name}.")

    return utils.coerce_to_coroutine_function(callback)


class Hook:

    def __init__(self, hook_name, parameters, return_type):
        """
        A set of functions to be called as a group upon a particular event.

        The signature of any functions added (via :func:`.callback` or :func:`__call__`
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

    def __call__(self, callback_: Callable) -> Callable:
        return self.callback(callback_)

    def callback(self, callback_: Callable) -> Callable:
        callback_params, return_type = _extract_params(callback_, extract_return=True)
        callback_ = _validate_parameters(self.name, callback_, self._params, callback_params)

        if self._return != return_type:
            raise TypeHintMismatch(f"Return type {return_type} of {callback_}\n"
                                   f"does not match expected type hint {self._return}")

        self.callbacks.append(callback_)
        return callback_

    def callback_until(self, hook_: "Hook"):

        def _temporary_callback(callback_):
            callback_ = self.callback(callback_)

            @hook_.callback
            def remove_callback():
                print(f"removing {callback_}")
                self.callbacks.remove(callback_)
                hook_.callbacks.remove(remove_callback)

            return callback_

        return _temporary_callback

    async def trigger(self, *args, **kwargs) -> List[Any]:
        return [await callback(*args, **kwargs) for callback in self.callbacks]


def hook(func: Callable):
    """Create a hook based on a function signature."""
    parameters, return_annotation = _extract_params(func, extract_return=True)
    return Hook(str(func), parameters, return_annotation)


def create_hook(name: str, *param_types, return_type=None):
    return Hook(name,
                [inspect.Parameter("", inspect.Parameter.POSITIONAL_ONLY, annotation=typ)
                 for typ in param_types],
                return_type=return_type)

