from sphinx.ext.autodoc import FunctionDocumenter
from sphinx.domains.python import PyFunction, PyObject
from sphinx.util.typing import OptionSpec
from docutils.parsers.rst import directives
from typing import Any
import re
import inspect


class FixtureDirective(PyFunction):
    option_spec: OptionSpec = PyObject.option_spec.copy()

    option_spec.update({
        'async': directives.flag,
        'generator': directives.flag,
    })

    def get_signature_prefix(self, sig: str) -> str:
        prefix = []
        if 'async' in self.options:
            prefix.append('async ')

        if 'generator' in self.options:
            prefix.append('generator ')

        prefix.append('fixture ')

        return ''.join(prefix)

    def needs_arglist(self) -> bool:
        return True

class FixtureDocumenter(FunctionDocumenter):
    objtype = "fixture"
    directivetype = "fixture"
    priority = 10 + FunctionDocumenter.priority

    @classmethod
    def can_document_member(cls,
                            member: Any, membername: str,
                            isattr: bool, parent: Any) -> bool:
        return hasattr(member, 'isfixture')

    
    def format_args(self, **kwargs: Any) -> str:
        args = super(FixtureDocumenter, self).format_args(**kwargs)

        return re.sub('\(.*?\)', '(...)', args)

    
    def add_directive_header(self, sig: str) -> None:
        sourcename = self.get_sourcename()
        super().add_directive_header(sig)

        if inspect.iscoroutinefunction(self.object):
            self.add_line('   :async:', sourcename)

        if inspect.isgeneratorfunction(self.object):
            self.add_line('   :generator:', sourcename)



def setup(app):
    app.setup_extension('sphinx.ext.autodoc')  # Require autodoc extension
    app.add_autodocumenter(FixtureDocumenter)
    app.add_directive('py:fixture', FixtureDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }