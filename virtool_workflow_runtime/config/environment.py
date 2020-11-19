"""Create fixtures for environment variable values."""
import os
from typing import Optional, Iterable, Type, Union

from virtool_workflow import WorkflowFixture

ENV_VARIABLE_TYPE = Union[str, int, bool]


def environment_variable_fixture(
        name: str,
        variable: str,
        default: Optional[ENV_VARIABLE_TYPE] = None,
        type_: Type[ENV_VARIABLE_TYPE] = str,
) -> WorkflowFixture:
    """
    Create a fixture exposing the value of an environment variable.

    :param name: The name of the fixture.
    :param variable: The name of the environment variable to be used.
    :param default: The default value to use if the environment variable is not set.
    :param type_: The expected type of the environment variable. Supported types are str, int, and bool.
    """

    def _fixture() -> Union[int, str, bool]:
        var = os.getenv(variable, default=default)
        if not var:
            if default is None:
                raise KeyError(f"{variable} is not set.")
            return default

        if type_ == bool:
            if var in ("True", "true", "Yes", "yes"):
                return True
            else:
                return False

        if type_ == int:
            return int(var)

        return var

    _fixture.__name__ = _fixture.__qualname__ = name

    class _Fixture(WorkflowFixture, param_name=name):
        default_value = default
        environment_variable = variable

        __fixture__ = _fixture

    _Fixture.__name__ = _Fixture.__qualname__ = name

    return _Fixture()




