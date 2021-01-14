"""Exceptions relating to workflow fixtures."""
import pprint
from inspect import Signature, getsourcefile, getsourcelines
from typing import Callable


class FixtureMultipleYield(ValueError):
    """Raised when a generator workflow fixture yields more than once."""


class FixtureNotAvailable(RuntimeError):
    """Raised when a required fixture is not available."""

    def _get_source_location(self, func: Callable):
        source, lineno = getsourcelines(func)
        source_file = getsourcefile(func)

        return source, f"{source_file}:{lineno}"

    def __init__(self, param_name: str, signature: Signature, func: Callable, scope, *args):
        """
        :param param_name: The name of the parameter/fixture which
            was not available
        :param signature: The signature of the function requiring the unavailable fixture.
        :param func: The function requiring the unavailable fixture.
        :param args: Arguments passed to ValueError's __init__
        :param kwargs: Keyword arguments passed to ValueError's __init__
        """
        self.param_name = param_name
        self.signature = signature
        self.func = func
        self.available_fixtures = {name: self._get_source_location(callable_)[1]
                                   for name, callable_ in scope.available.items()}
        super().__init__(*args)

    def __str__(self):
        _, location = self._get_source_location(self.func)
        available_fixture_lines = "\n".join(f'{name}: \n {loc}'
                                            for name, loc in self.available_fixtures.items())
        return f"'{self.param_name}' is not available as a workflow fixture.\n" \
               f"{location}\n"\
               f"Available fixtures:\n {available_fixture_lines}\n"



