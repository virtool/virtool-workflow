import virtool_workflow

from imported import foo, bar
from package import module_in_package


@virtool_workflow.step
def _use_foo_and_bar(results):
    results[foo] = foo
    results[bar] = bar
    results["variable"] = module_in_package.variable_in_module

