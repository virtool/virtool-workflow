from typing import Protocol
from virtool_workflow import fixture
from typing import Any


class ReturnProtocol(Protocol):
    """A showcase return protocol"""

    def __call__(self, a: int, b: str, c: Any, d: str = "default") -> Any:
        """
        A function that does something...

        :param a: An argument to the function.
        :param b: An argument to the function.
        :param c: An argument to the function.

        :return: Anything, but probably nothing.
        :raises NotImplementedError: Every time.
        """


@fixture
def regular_fixture(a, b, c) -> int:
    """An example fixture."""
    ...


@fixture(protocol=ReturnProtocol)
def protocol_fixture(regular_fixture) -> ReturnProtocol:
    ...
