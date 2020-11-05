import os
from virtool_workflow_runtime.config import environment
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from virtool_workflow_runtime.config.configuration import VirtoolConfiguration

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


async def test_use_config():

    with WorkflowFixtureScope() as fixtures:
        redis_connection_string = await fixtures.instantiate(environment.redis_connection_string)
        config: VirtoolConfiguration = await fixtures.instantiate(VirtoolConfiguration)

        assert config.redis_connection_string == environment.redis_connection_string()
        assert id(redis_connection_string) == id(config.redis_connection_string)
        assert id(fixtures["no_sentry"]) == id(config.no_sentry)
        assert config.no_sentry == environment.no_sentry()
        assert config.mem == environment.mem()
        assert config.mongo_connection_string == environment.db_connection_string()
