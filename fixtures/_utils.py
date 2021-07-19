import inspect


def get_defaults(argspec: inspect.FullArgSpec) -> dict:
    """Map the arguments from the argspec to their default values."""
    if not argspec.defaults:
        return {}

    args_with_default = argspec.args[-len(argspec.defaults):]
    return {key: value for key, value in zip(
        args_with_default, argspec.defaults)}


def get_arg_spec(function, follow_wrapped=False) -> inspect.FullArgSpec:
    """
    Get the arg spec for a function.

    :param function: A function.
    :param follow_wrapped: Follow `__wrapped__`, defaults to False.

    :return: A :class:`inspect.FullArgSpec`
    """
    if follow_wrapped:
        function = inspect.unwrap(function)
    return inspect.getfullargspec(function)
