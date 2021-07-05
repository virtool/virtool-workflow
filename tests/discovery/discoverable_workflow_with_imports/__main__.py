from virtool_workflow import step
from local_module import foo, bar


@step
def _step(results):
    results["foo"] = foo
    results["bar"] = bar
