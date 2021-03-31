from typing import Callable

from virtool_workflow.config.configuration import ConfigFixture
from virtool_workflow.fixtures.scope import FixtureGroup


class ConfigFixtureGroup(FixtureGroup):
    def fixture(self, func: Callable = None, type_=str, default=None):
        """Create a config fixture based on the given callable and include it in this :class:`FixtureGroup`."""
        if func is None:

            def _decorator(func: Callable):
                return self.fixture(func, type_, default)

            return _decorator

        env_name = "VT_" + func.__name__.upper().replace("-", "_")
        help_text = func.__doc__

        _fixture = ConfigFixture(
            name=func.__name__,
            env=env_name,
            type_=type_,
            default=default,
            transform=func,
            help_=help_text,
        )

        return super().fixture(_fixture)

    def add_options(func: Callable):
        for name, fixture in self.items():
            option_name = fixture.name.replace("_", "-")
            func = click.option(option_name, type=fixture.type, help=fixture.help)(func)

        return func
