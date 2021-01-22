import os
from virtool_workflow_runtime.config import configuration
from virtool_workflow.fixtures.scope import FixtureScope


@configuration.config_fixture("EDITOR", type_=str, default="/usr/bin/nano")
def editor(_):
    ...


async def test_environment_variable_fixture(runtime):
    with runtime.scope as fixtures:
        editor_ = await fixtures.get_or_instantiate("editor")
        assert editor_ == os.getenv("EDITOR", default="/usr/bin/nano")


async def test_types(runtime):
    with runtime.scope as fixtures:
        @configuration.config_fixture("TEST_ENV_VARIABLE", type_=bool, default=False)
        def boolean(_):
            ...

        value = await fixtures.instantiate(boolean)

        assert not value

        os.environ["TEST_ENV_VARIABLE"] = "yes"

        assert os.getenv("TEST_ENV_VARIABLE") == "yes"

        del fixtures["boolean"]

        value = await fixtures.instantiate(boolean)

        assert value

    with FixtureScope() as fixtures:
        @configuration.config_fixture("TEST_ENV_VARIABLE", type_=int)
        def integer(_):
            ...

        os.environ["TEST_ENV_VARIABLE"] = "49"
        integer_ = await fixtures.instantiate(integer)

        assert integer_ == 49

