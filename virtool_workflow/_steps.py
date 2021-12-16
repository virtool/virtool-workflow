from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Awaitable, Callable
from textwrap import dedent

from virtool_workflow.utils import coerce_to_coroutine_function


def get_display_name(call: Callable[..., Any]):
    """
    Get the display name for a step function based on the function name.

    Underscores will be replaced by spaces and each word will be capitalized.
    
    :param call: The calable for the step function
    :return: The presentation name as a string
    """
    name = call.__name__
    return name.replace("_", " ").title()

def get_description(call: Callable[..., Any]) -> str:
    """
    Extract the description for a step function from the docstring.
    
    Lines starting with sphinx tags such as :param: are removed and 
    trailing whitespace is stripped.

    :param call: The step function
    :return str: The step description
    :raise ValueError: When `call` does not have a docstring
    """
    if call.__doc__ is None:
        raise ValueError(f"{call} does not have a docstring")

    description = re.sub(
        pattern=r"^\s*:.*$", 
        repl="", 
        string=call.__doc__, 
        flags=re.MULTILINE,
    )
    
    return "\n".join(line.strip(" ") for line in description.split("\n") if line)
    

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
    call: Callable[..., Awaitable[Any]]
    

    @classmethod
    def from_callable(cls, 
        call: Callable[..., Any],
        *, 
        display_name: str = None, 
        description: str = None
    ) -> WorkflowStep:
        """
        Create a WorkflowStep from a callable. 
        
        :param call: The callable to be used.
        :param display_name: The display name to be used, if None then a display name
            will be created based on the function name of `call`.
        :param description: A text description of the step. If None then the docstring
            `call` will be used.
        """
        call = coerce_to_coroutine_function(call)
        display_name = display_name or get_display_name(call)
        try:
            description = description or get_description(call)
        except ValueError:
            description = ""

        return cls(
            display_name=display_name,
            description=description,
            call=call,
        )
        
    async def __call__(self, *args, **kwargs):
        return await self.call(*args, **kwargs)
