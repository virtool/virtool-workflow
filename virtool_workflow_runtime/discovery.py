from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from types import ModuleType
from typing import List, Union, Iterable, Tuple, Optional

from virtool_workflow import Workflow, WorkflowFixture

__fixtures__type__ = Iterable[
    Union[
        str,
        Iterable[str]
    ]
]


def _import_module_from_file(module_name: str, path: Path) -> ModuleType:
    """
    Import a module from a file

    :param module_name: The name of the python module.
    :param path: The :class:`pathlib.Path` of the python file
    :returns: The loaded python module.
    """
    spec = spec_from_file_location(module_name, path)
    module = spec.loader.load_module(module_from_spec(spec).__name__)
    return module


def discover_fixtures(module: Union[Path, ModuleType]) -> List[WorkflowFixture]:
    """
    Find all instances of :class:`WorkflowFixture` in a python module.

    :param module: The path to the python module to import
    :return: A list of all :class:`WorkflowFixture` instances contained
        in the module
    """
    if isinstance(module, Path):
        module = _import_module_from_file(module.name.rstrip(module.suffix), module)

    return [attr for attr in module.__dict__.values() if isinstance(attr, WorkflowFixture)]


def load_fixtures_from__fixtures__(path: Path):
    module = _import_module_from_file(path.name.rstrip(path.suffix), path)

    __fixtures__ = getattr(module, "__fixtures__", [])

    fixtures = []
    for fixture_set in __fixtures__:
        if isinstance(fixture_set, str):
            fixtures.extend(discover_fixtures(import_module(fixture_set)))
        else:
            iter_ = iter(fixture_set)
            module = import_module(next(iter_))
            fixtures.extend(getattr(module, name) for name in iter_
                            if isinstance(getattr(module, name), WorkflowFixture))

    return fixtures


def discover_workflow(path: Path) -> Workflow:
    """
    Find a instance of virtool_workflow.Workflow in the python module located at the given path.

    :param path: The :class:`pathlib.Path` to the python file containing the module
    :returns: The first instance of :class:`virtool_workflow.Workflow` occurring in `dir(module)`

    :raises StopIteration: When no instance of virtool_workflow.Workflow can be found.
    """
    module = _import_module_from_file(path.name.rstrip(path.suffix), path)

    return next(attr for attr in module.__dict__.values() if isinstance(attr, Workflow))


def run_discovery(
        path: Path,
        fixture_path: Optional[Path] = None
) -> Tuple[Workflow, List[WorkflowFixture]]:
    fixtures = load_fixtures_from__fixtures__(Path(__file__).parent/"autoload.py")

    fixtures.extend(load_fixtures_from__fixtures__(path))

    if fixture_path and fixture_path.exists():
        fixtures.extend(discover_fixtures(fixture_path))

    workflow = discover_workflow(path)

    return workflow, fixtures

