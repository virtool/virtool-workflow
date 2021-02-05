from virtool_workflow.fixtures import workflow_scope, fixture
from virtool_workflow import hooks


@fixture
def generator_fixture():
    yield True
    raise ValueError()


async def test_workflow_scope_closes():
    workflow_scope["item"] = "value"

    await hooks.on_finish.trigger(workflow_scope)

    assert "item" not in workflow_scope


async def test_generator_fixture_finishes():
    await workflow_scope.instantiate(generator_fixture)

    assert workflow_scope["generator_fixture"]

    try:
        await hooks.on_finish.trigger(workflow_scope)
    except ValueError:
        return

    assert False







