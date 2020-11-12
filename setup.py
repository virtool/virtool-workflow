"""setup.py for virtool_workflow_runtime and virtool_workflow."""
from pathlib import Path

from setuptools import setup, find_packages

AUTHORS = ["Ian Boyes", "Blake Smith"]

CLASSIFIERS = [
    "Topic :: Software Development :: Libraries",
    "Programming Language:: Python:: 3.6",
]

PACKAGES = find_packages(exclude="tests")


INSTALL_REQUIRES = [
    "virtool_core @ git+https://github.com/virtool/virtool-core",
    "click",
    "motor",
    "uvloop",
    "aiohttp",
    "aioredis==1.3.1",
]


ENTRY_POINTS = {
    "console_scripts": [
        "workflow = virtool_workflow_runtime.cli:cli_main",
    ]
}

setup(
    name="virtool_workflow",
    description="An SDK and runtime for creating Virtool workflows",
    long_description=Path("README.md").read_text(),
    url="https://github.com/virtool/virtool-workflow",
    author=", ".join(AUTHORS),
    license="MIT",
    platforms="linux",
    packages=PACKAGES,
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.6",
    entry_points=ENTRY_POINTS
)
