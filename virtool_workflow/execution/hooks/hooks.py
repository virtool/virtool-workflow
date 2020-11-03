import inspect
from typing import List, Any, Callable, Type

from virtool_workflow import utils


class IncompatibleCallback(ValueError):
    """Raised when a callback function is not compatible with a Hook"""

    def __init__(self, callback, *args):
        super().__init__(*args)
        self.callback = callback

    def __str__(self):
        s = super().__str__()
        code, line_number = inspect.getsourcelines(self.callback)
        code = "".join(code)
        file = inspect.getsourcefile(self.callback)
        return f"{s}\n\n{file}:{line_number}\n\n{code}"


class ParameterMismatch(IncompatibleCallback):
    """Raised when the parameters of a callback function are not compatible with a Hook."""


class TypeHintMismatch(ParameterMismatch):
    """
    Raised when the type hints of a positional parameter
    do not match between a callback function and a hook definition.
    """


def _extract_params(func: Callable, extract_return: bool = False):
    """Extract parameters from the signature of a function."""
    signature = inspect.signature(func)
    parameters = [param.annotation for param in signature.parameters.values()]
    if extract_return:
        return parameters, signature.return_annotation
    return parameters


def _validate_parameters(
        hook_name: str,
        callback: Callable,
        hook_params: List[Type],
        callback_params: List[Type]
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
        raise ParameterMismatch(callback, f"{callback} takes {len(callback_params)} parameters "
                                f"where {hook_name} takes {len(hook_params)} parameters.")

    for hook_param, callback_param in zip(hook_params, callback_params):
        if hook_param is inspect.Parameter.empty or \
                callback_param is inspect.Parameter.empty:
            continue

        if hook_param != callback_param:
            raise TypeHintMismatch(callback, f"({callback_param}) of {callback} does not "
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

    def callback(self, callback_: Callable = None, until=None, once=False):
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

        return cb

    __call__ = callback

    def _callback(self, callback_: Callable) -> Callable:
        callback_params, return_type = _extract_params(callback_, extract_return=True)
        callback_ = _validate_parameters(self.name, callback_, self._params, callback_params)

        if self._return != inspect.Parameter.empty \
                and return_type != inspect.Parameter.empty \
                and self._return != return_type:
            raise TypeHintMismatch(f"Return type {return_type} of {callback_}\n"
                                   f"does not match expected type hint {self._return}")

        self.callbacks.append(callback_)
        return callback_

    def _callback_until(self, hook_: "Hook"):

        def _temporary_callback(callback_):
            callback_ = self._callback(callback_)

            @hook_._callback
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
