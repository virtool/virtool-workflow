import os

from virtool_workflow.config.fixtures import options


@options.fixture(default="/usr/bin/nano")
def editor(_):
    ...


async def test_environment_variable_fixture():
    editor_ = editor()
    assert editor_ == os.getenv("EDITOR", default="/usr/bin/nano")


async def test_types(runtime):
    @options.fixture(type_=bool, default=False)
    def boolean(_):
        ...

    value = await runtime.instantiate(boolean)
    assert not value

    os.environ["BOOLEAN"] = "yes"
    assert os.getenv("BOOLEAN") == "yes"

    del runtime["boolean"]

    value = await runtime.instantiate(boolean)

    assert value

    @configuration.config_fixture("BOOLEAN", type_=int)
    def integer(_):
        ...

    os.environ["BOOLEAN"] = "49"
    integer_ = await runtime.instantiate(integer)

    assert integer_ == 49
