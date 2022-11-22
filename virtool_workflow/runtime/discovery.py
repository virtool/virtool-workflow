import sys
from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
from logging import getLogger
from pathlib import Path
from types import ModuleType
from typing import Union, List, Callable

from virtool_workflow import Workflow
from virtool_workflow.decorators import collect

logger = getLogger("runtime")


def load_workflow_and_fixtures():
    logger.info("Importing workflow.py")
    try:
        workflow = discover_workflow(Path("./workflow.py"))
    except FileNotFoundError:
        logger.fatal("Could not find workflow.py")
        sys.exit(1)

    logger.info("Importing fixtures.py")
    fixtures_path = Path("./fixtures.py")

    try:
        import_module_from_file(fixtures_path.name.rstrip(".py"), fixtures_path)
    except FileNotFoundError:
        logger.info("No fixtures.py found")

    for name in (
        "virtool_workflow.builtin_fixtures",
        "virtool_workflow.analysis.fixtures",
        "virtool_workflow.runtime.providers",
    ):
        module = import_module(name)
        logger.debug(f"Imported {module}")

    return workflow


def import_module_from_file(module_name: str, path: Path) -> ModuleType:
    """
    Import a module from a file.

    The parent directory of `path` will also be added to `sys.path` prior to importing.
    This ensures that modules and packages defined in that directory can be properly
    imported.

    :param module_name: The module's name.
    :param path: The module's path.
    :returns: The loaded module.
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
