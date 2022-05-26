class IllegalJobArguments(ValueError):
    """The `job.args` dict is in an illegal state."""

    ...


class MissingJobArgument(ValueError):
    """The `job.args` dict is missing a required key for some funcionality."""

    ...
