import os

from virtool_workflow.config import configuration


@configuration.config_fixture("EDITOR", type_=str, default="/usr/bin/nano")
def editor(_):
    ...


async def test_environment_variable_fixture():
    editor_ = editor()
    assert editor_ == os.getenv("EDITOR", default="/usr/bin/nano")


async def test_types(runtime):
    @configuration.config_fixture("TEST_ENV_VARIABLE", type_=bool, default=False)
    def boolean(_):
        ...

    value = await runtime.instantiate(boolean)
    assert not value

    os.environ["TEST_ENV_VARIABLE"] = "yes"
    assert os.getenv("TEST_ENV_VARIABLE") == "yes"

    del runtime["boolean"]

    value = await runtime.instantiate(boolean)

    assert value

    @configuration.config_fixture("TEST_ENV_VARIABLE", type_=int)
    def integer(_):
        ...

    os.environ["TEST_ENV_VARIABLE"] = "49"
    integer_ = await runtime.instantiate(integer)

    assert integer_ == 49
