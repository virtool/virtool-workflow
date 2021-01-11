from abc import ABC, abstractmethod


class AbstractSampleProvider(ABC):

    @abstractmethod
    def recalculate_workflow_tags(self):
        """Recalculate workflow tags for samples associated with the current job."""
        ...

