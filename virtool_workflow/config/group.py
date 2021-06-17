from typing import Callable
from functools import wraps

import click

from virtool_workflow.fixtures.scope import FixtureGroup


class ConfigFixtureGroup(FixtureGroup):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = []

    def fixture(self, type_=str, default=None):

        def _deco(func):
            def _fixture():
                try:
                    return func(_fixture.override_value)
                except AttributeError:
                    return func(default)

            _fixture.__name__ = _fixture.__qualname__ = func.__name__

            _fixture = super(ConfigFixtureGroup, self).fixture(_fixture)

            # wraps copys the signature of `func` to `_fixture`
            # this is required for sphinx to work properly, but
            # it causes problems with fixture binding.
            # so we only wrap the function on return
            return wraps(func)(_fixture)

        return _deco

    def add_options(self, func: Callable):
        """
        Add click options based on the config fixtures of this group.

        :param func: A `click` command or group.
        """
        for name, fixture in self.items():
            option_name = "--" + fixture.name.replace("_", "-")
            func = click.option(
                option_name, type=fixture.type, help=fixture.help)(func)

        return func
