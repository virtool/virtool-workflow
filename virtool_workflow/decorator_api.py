import sys
from virtool_workflow import Workflow
from types import ModuleType


class DelegatedAttribute:

    def __init__(self, delegate_name):
        self._delegate_name = delegate_name

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        if instance:
            return getattr(getattr(instance, self._delegate_name), self._name)
        else:
            return getattr(getattr(owner, self._delegate_name), self._name)


workflow = Workflow


class WorkflowDecoratorModule(ModuleType):
    _workflow = Workflow()
    startup = DelegatedAttribute("_workflow")
    step = DelegatedAttribute("_workflow")
    cleanup = DelegatedAttribute("_workflow")


sys.modules[__name__] = WorkflowDecoratorModule(__name__, __doc__)





