import os
from virtool_workflow_runtime.config import environment
from virtool_workflow.fixtures.scope import WorkflowFixtureScope

editor = environment.environment_variable_fixture("editor", "EDITOR", type_=str, default="/usr/bin/nano")


async def test_environment_variable_fixture():
    with WorkflowFixtureScope() as fixtures:
        editor_ = await fixtures.get_or_instantiate("editor")
        assert editor_ == os.getenv("EDITOR", default="/usr/bin/nano")


async def test_types():
    with WorkflowFixtureScope() as fixtures:
        boolean = environment.environment_variable_fixture("boolean",
                                                           "TEST_ENV_VARIABLE",
                                                           type_=bool,
                                                           default=False)

        value = await fixtures.instantiate(boolean)

        assert not value

        os.environ["TEST_ENV_VARIABLE"] = "yes"

        assert os.getenv("TEST_ENV_VARIABLE") == "yes"

        del fixtures["boolean"]

        value = await fixtures.instantiate(boolean)

        assert value

    with WorkflowFixtureScope() as fixtures:
        integer = environment.environment_variable_fixture(
            "integer", "TEST_ENV_VARIABLE", type_=int)

        os.environ["TEST_ENV_VARIABLE"] = "49"
        integer_ = await fixtures.instantiate(integer)

        assert integer_ == 49

