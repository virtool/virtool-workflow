"""Pytest-style fixtures for use in Virtool Workflows."""
import logging
from typing import Callable

from .providers import FixtureGroup

logger = logging.getLogger(__name__)


workflow_fixtures = FixtureGroup()
"""Global dict containing all defined workflow fixtures."""


def fixture(func: Callable=None, **kwargs):
    """
    Workflow fixtures can be either async or standard functions. They can also be
    generator functions which only yield a single value. Any code after the yield statement
    will be executed when the :class:`virtool_workflow.WorkflowFixtureScope` closes.

    Workflow fixtures may accept other fixtures as parameters, as long as they are available within
    the current `virtool_workflow.WorkflowFixtureScope`.

    :param func: A function returning some value to be used as a workflow fixture
    :return: The unchanged :obj:`func` function.
    """
    if func is None:
        return lambda func_: fixture(func_, **kwargs)
    logger.debug(f"Defined a new fixture `{func.__name__}`")
    return workflow_fixtures.fixture(func, **kwargs)

