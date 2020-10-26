"""Exceptions relating to workflow fixtures."""
from inspect import Signature


class WorkflowFixtureMultipleYield(ValueError):
    """Raised when a generator workflow fixture yields more than once."""


class WorkflowFixtureNotAvailable(RuntimeError):
    """Raised when a required fixture is not available."""

    def __init__(self, param_name: str, signature: Signature, *args, **kwargs):
        """
        :param param_name: The name of the parameter/fixture which
            was not available
        :param args: Arguments passed to ValueError's __init__
        :param kwargs: Keyword arguments passed to ValueError's __init__
        """
        self.param_name = param_name
        self.signature = signature
        super.__init__(*args, **kwargs)

