from contextlib import asynccontextmanager
from virtool_workflow.execution.hooks import FixtureHook
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow.fixtures.scoping import workflow_scope


@asynccontextmanager
def trigger(on_enter: FixtureHook,
            on_exit: FixtureHook,
            scope: FixtureScope = workflow_scope,
            enter_args: dict = None,
            exit_args: dict = None):
    enter_args = enter_args or {}
    exit_args = exit_args or {}

    await on_enter.trigger(scope=scope, **enter_args)
    try:
        yield
    finally:
        await on_exit.trigger(scope=scope, **exit_args)




