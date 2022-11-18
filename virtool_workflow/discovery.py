"""Find workflows and fixtures from python modules."""
import sys
from importlib.util import spec_from_file_location, module_from_spec
from logging import getLogger
from pathlib import Path
from types import ModuleType
from typing import Callable
from typing import List, Union, Tuple, Optional

from virtool_workflow.decorators import collect
from virtool_workflow.workflow import Workflow

logger = getLogger("runtime")


def import_module_from_file(module_name: str, path: Path) -> ModuleType:
    """
    Import a module from a file.

    The parent directory of `path` will also be added to `sys.path`
    prior to importing. This ensures that modules and packages defined
    in that directory can be properly imported.

    :param module_name: The name of the python module.
    :param path: The :class:`pathlib.Path` of the python file
    :returns: The loaded python module.
    """
    module_parent = str(path.parent)
    sys.path.append(module_parent)
    spec = spec_from_file_location(module_name, path)
    if spec is None:
        raise ImportError(f"could not import {path}")
    module = spec.loader.load_module(module_from_spec(spec).__name__)
    sys.path.remove(module_parent)
    return module


def discover_fixtures(module: Union[Path, ModuleType]) -> List[Callable]:
    """
    Find all instances of :class:`Workflow` in a python module.

    :param module: The path to the python module to import
    :return: A list of all fixture instances contained in the module
    """

    if isinstance(module, Path):
        module = import_module_from_file(module.name.rstrip(module.suffix), module)

    return [attr for attr in module.__dict__.values() if isinstance(attr, Callable)]


def discover_workflow(path: Path) -> Workflow:
    """
    Find an instance of :class:`.Workflow` in the python module located at the given
    path.

    :param path: The path to a Python module.
    :return: The first :class:`.Workflow` class in the module.
    :raises ValueError: No workflow definition found.
    """
    module = import_module_from_file(path.name.rstrip(path.suffix), path)

    try:
        return next(
            attr for attr in module.__dict__.values() if isinstance(attr, Workflow)
        )
    except StopIteration:
        return collect(module)


def run_discovery(
    path: Path, fixture_path: Optional[Path] = None
) -> Tuple[Workflow, List[Callable]]:
    """
    Discover a workflow and fixtures from the given path(s).

    :param path: A Path to the workflow module
    :param fixture_path: A Path to a module conaining addtional fitures.
    :return: A :class:`Workflow` instance and a list of fixtures.
    """
    logger.info("Discovering workflow")

    fixtures = []
    if fixture_path and fixture_path.exists():
        fixtures.extend(discover_fixtures(fixture_path))
        logger.info(f"Loaded fixture file path={fixture_path}")

    workflow = discover_workflow(path)

    logger.info(f"Workflow discovery complete")

    return workflow, fixtures
