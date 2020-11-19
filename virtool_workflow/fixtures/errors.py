"""Exceptions relating to workflow fixtures."""
import pprint
from inspect import Signature, getsourcefile, getsourcelines
from typing import Callable
from virtool_workflow.fixtures.workflow_fixture import WorkflowFixture


class WorkflowFixtureMultipleYield(ValueError):
    """Raised when a generator workflow fixture yields more than once."""


class WorkflowFixtureNotAvailable(RuntimeError):
    """Raised when a required fixture is not available."""

    def __init__(self, param_name: str, signature: Signature, func: Callable, *args):
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
        self.available_fixtures = WorkflowFixture.types()
        super().__init__(*args)

    def __str__(self):
        source, lineno = getsourcelines(self.func)
        source = "".join(source)
        return f"'{self.param_name}' is not available as a workflow fixture.\n" \
               f"Ensure that the corresponding fixture has been imported.\n\n" \
               f"{getsourcefile(self.func)}:{lineno}\n"\
               f"{source}\n\n" \
               f"Available fixtures:\n {pprint.pformat(self.available_fixtures)}\n"



