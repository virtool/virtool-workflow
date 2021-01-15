"""Pytest-style fixtures for use in Virtool Workflows."""
import logging
from typing import Callable
from .providers import CallableProviderDict

logger = logging.getLogger(__name__)


workflow_fixtures = CallableProviderDict()
"""Global dict containing all defined workflow fixtures."""


def fixture(func: Callable):
    """
    Workflow fixtures can be either async or standard functions. They can also be
    generator functions which only yield a single value. Any code after the yield statement
    will be executed when the :class:`virtool_workflow.WorkflowFixtureScope` closes.

    Workflow fixtures may accept other fixtures as parameters, as long as they are available within
    the current `virtool_workflow.WorkflowFixtureScope`.

    :param func: A function returning some value to be used as a workflow fixture
    :return: The unchanged :obj:`func` function.
    """
    logger.debug(f"Defined a new fixture `{func.__name__}`")
    workflow_fixtures[func.__name__] = func
    return func

