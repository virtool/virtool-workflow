from virtool_workflow import step


@step
def test_workflow_step(results):
    results["done"] = True


@step
def use_indexes(indexes):
    ...
