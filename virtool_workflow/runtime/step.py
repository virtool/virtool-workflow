from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from virtool_workflow.runtime.utils import coerce_to_coroutine_function


def get_display_name(function: Callable[..., Any]):
    """
    Get the display name for a step function based on the function name.

    Underscores will be replaced by spaces and each word will be capitalized.

    :param call: The calable for the step function
    :return: The presentation name as a string
    """
    name = function.__name__
    return name.replace("_", " ").title()


def get_description(function: Callable[..., Any]) -> str:
    """
    Extract the first line of the docstring as a description for a step function.

    :param call: The step function
    :return str: The step description
    :raise ValueError: When `call` does not have a docstring
    """
    if function.__doc__ is None:
        raise ValueError(f"{function} does not have a docstring")

    return function.__doc__.strip().split("\n")[0]


@dataclass(frozen=True)
class WorkflowStep:
    """
    Metadata for a workflow step.

    :param name: The presentation name for the step.
    :param description: The description of the step.
    :param call: The async step function.
    """

    display_name: str
    description: str
    function: Callable[..., Awaitable[Any]]

    @classmethod
    def from_callable(
        cls,
        function: Callable[..., Any],
        *,
        display_name: str = None,
        description: str = None,
    ) -> WorkflowStep:
        """
        Create a WorkflowStep from a callable.

        :param call: The callable to be used.
        :param display_name: The display name to be used, if None then a display name
            will be created based on the function name of `call`.
        :param description: A text description of the step. If None then the docstring
            `call` will be used.
        """
        function = coerce_to_coroutine_function(function)
        display_name = display_name or get_display_name(function)
        try:
            description = description or get_description(function)
        except ValueError:
            description = ""

        return cls(
            display_name=display_name,
            description=description,
            function=function,
        )

    async def __call__(self, *args, **kwargs):
        return await self.function(*args, **kwargs)
