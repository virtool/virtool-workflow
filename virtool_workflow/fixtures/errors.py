"""Exceptions relating to workflow fixtures."""
from inspect import Signature, getsourcefile, getsourcelines
from typing import Callable


class FixtureMultipleYield(ValueError):
    """Raised when a generator workflow fixture yields more than once."""


class FixtureNotAvailable(RuntimeError):
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

    def __init__(self, exception_message: str, signature: Signature, func: Callable, scope, *args):
        """
        :param message: The message of the cause exception.
        :param signature: The signature of the function requiring the unavailable fixture.
        :param func: The function requiring the unavailable fixture.
        :param args: Arguments passed to ValueError's __init__
        """
        self.message = exception_message
        self.signature = signature
        self.func = func
        self.available_fixtures = {
            name: self._get_source_location(callable_)[1]
            if callable(callable_) else str(callable_)
            for name, callable_ in scope.available.items()
        }

        self.available_fixtures = {k: v or "Source location not available" for k, v in self.available_fixtures.items()}
        super().__init__(*args)

    def __str__(self):
        _, location = self._get_source_location(self.func)
        available_fixture_lines = "\n".join(f'{name}: \n   {loc}'
                                            for name, loc in self.available_fixtures.items())
        return f"'\n{self.message}\n" \
               f"{location if location else ''}\n" \
               f"Available fixtures:\n {available_fixture_lines}\n"
