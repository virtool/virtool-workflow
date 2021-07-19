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


def get_source_location(func: callable):
    """
    Get the source location of a function.

    :param func: A function.
    :return: A tuple of (List[str], str) giving the source lines of the function
             and it's location as a string "/path/to/file:{linenumber}".
    """
    try:
        source, lineno = inspect.getsourcelines(func)
        source_file = inspect.getsourcefile(func)
    except (TypeError, OSError):  # func may be a Callable class
        if not hasattr(func, "__call__"):
            raise

        source, lineno = inspect.getsourcelines(func.__call__)
        source_file = inspect.getsourcefile(func.__call__)

    return source, f"{source_file}:{lineno}"
