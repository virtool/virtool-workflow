from typing import Callable
from functools import wraps

import click

from virtool_workflow.fixtures.scope import FixtureGroup


class ConfigFixtureGroup(FixtureGroup):
    """
    A :class:`FixtureGroup` which creates click options when fixtures are added.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = []

    def fixture(
            self,
            default=None,
            short_name: str = None,
            is_argument=False,
            **kwargs
    ):
        """
        Create a configuration fixture decorator.

        Invoking the decorator will result in the creation of:

        1. A click argument/option
            a. It's name taken from the target function's name
            b. It's help taken from the target function's docstring
        2. A fixture providing access to the value of the click argument/option

        The target for the decorator will take a single argument corresponding
        to the expected value returned by click. The return value of the target
        function will be used as the value of the fixture.

        :param default: The default value for the fixture.
        :param short_name: The short version of the click option name.
        :param is_argument: A flag indicating that a click argument should
                            be created instead of a click option.
        :param kwargs: Any additional arguments for the click option/argument.

        :return: A decorator which will create a click option/argument and
                 a fixture providing access to the value of the option/argument.

        """

        def _deco(func):
            if is_argument:

                self.options.append(
                    click.argument(
                        func.__name__,
                        default=default,
                        **kwargs
                    )
                )
            else:
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
                        help=func.__doc__ or "",
                        **kwargs,
                    )
                )

            @wraps(func)
            def _fixture():
                try:
                    value = func(_fixture.__value__)
                    return value if value is not None else _fixture.__value__
                except AttributeError:
                    value = func(default)
                    return value if value is not None else default

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
