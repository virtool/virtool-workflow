from typing import Callable
from functools import wraps

import click

from virtool_workflow.fixtures.scope import FixtureGroup


class ConfigFixtureGroup(FixtureGroup):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = []

    def fixture(self, default=None, short_name: str = None, **kwargs):

        def _deco(func):
            opt_name = "--" + func.__name__.replace("_", "-")
            names = (
                (short_name, opt_name)
                if short_name is not None
                else (opt_name,)
            )

            self.options.append(
                click.option(
                    *names,
                    envvar="VT_" + func.__name__.upper(),
                    default=default,
                    help=func.__doc__,
                    **kwargs,
                )
            )

            @wraps(func)
            def _fixture():
                try:
                    return func(_fixture.override_value)
                except AttributeError:
                    return func(default)

            # Use signature of wrapper when fixture binding
            _fixture.__follow_wrapped__ = False

            return super(ConfigFixtureGroup, self).fixture(_fixture)

        return _deco

    def add_options(self, func: Callable):
        """
        Add click options based on the config fixtures of this group.

        :param func: A `click` command or group.
        """
        for option in self.options:
            func = option(func)

        return func
