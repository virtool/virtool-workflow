"""Exceptions relating to workflow fixtures."""
from inspect import getsourcefile, getsourcelines
import inspect
from typing import Callable


class FixtureMultipleYield(ValueError):
    """Raised when a generator workflow fixture yields more than once."""


class FixtureNotFound(KeyError):
    def __init__(self, name, scope):
        super().__init__(f"{name} is not a fixture.",
                         f"Available: {', '.join(scope.available.keys())}")


class FixtureBindingError(Exception):
    """Raised when a required fixture is not available."""

    def _get_source_location(self, func: Callable):
        try:
            try:
                source, lineno = getsourcelines(func)
                source_file = getsourcefile(func)
            except (TypeError, OSError):  # func may be a Callable class
                if hasattr(func, "__call__"):
                    source, lineno = getsourcelines(func.__call__)
                    source_file = getsourcefile(func.__call__)
                else:
                    raise

            return source, f"{source_file}:{lineno}"
        except TypeError:
            return None, None

    def __init__(self, func: Callable, key: str,
                 reason="Exception occurred while binding fixtures."):
        """
        :param func: The function requiring the unavailable fixture
        :param key: The name of the fixture which could not be instantiated
        :param reason: The reason for the error
        """
        self.func = func
        self.key = key
        self.reason = reason

        _, func_location = self._get_source_location(func)
        message = (f"Failed to bind fixture '{key}'\r\n"
                   f"Reason: {reason}\r\n"
                   f"Function: {func} \r\n"
                   f"Source Location: {func_location}\r\n")
        super().__init__(message)

    def __str__(self):
        return self.args[0]
