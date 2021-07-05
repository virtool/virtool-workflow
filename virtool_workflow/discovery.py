"""Find workflows and fixtures from python modules."""
import sys

import logging
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from types import ModuleType
from typing import Callable
from typing import List, Union, Tuple, Optional

from virtool_workflow.decorator_api import collect
from virtool_workflow.workflow import Workflow


logger = logging.getLogger(__name__)


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
        module = import_module_from_file(
            module.name.rstrip(module.suffix), module)

    return [
        attr for attr in module.__dict__.values()
        if isinstance(attr, Callable)
    ]


def discover_workflow(path: Path) -> Workflow:
    """
    Find a instance of virtool_workflow.Workflow in the
    python module located at the given path.

    :param path: The :class:`pathlib.Path` to the python file
                 containing the module.
    :returns: The first instance of :class:`virtool_workflow.Workflow`
              occurring in `dir(module)`

    :raises StopIteration:
        When no instance of virtool_workflow.Workflow can be found.
    """
    module = import_module_from_file(path.name.rstrip(path.suffix), path)

    try:
        return next(
            attr for attr in module.__dict__.values()
            if isinstance(attr, Workflow)
        )
    except StopIteration:
        return collect(module)


def run_discovery(
        path: Path,
        fixture_path: Optional[Path] = None
) -> Tuple[Workflow, List[Callable]]:
    """
    Discover a workflow and fixtures from the given path(s).

    :param path: A Path to the workflow module
    :param fixture_path: A Path to a module conaining addtional fitures.
    :return: A :class:`Workflow` instance and a list of fixtures.
    """
    logger.info("Beginning workflow discovery.")

    fixtures = []
    if fixture_path and fixture_path.exists():
        fixtures.extend(discover_fixtures(fixture_path))

        logger.info(f"Loaded {fixture_path}")

    workflow = discover_workflow(path)

    logger.info(f"Discovered Workflow {workflow}")

    return workflow, fixtures
