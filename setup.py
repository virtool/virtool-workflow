"""setup.py for virtool_workflow_runtime and virtool_workflow."""
from pathlib import Path

from setuptools import setup, find_packages

AUTHORS = ["Ian Boyes", "Blake Smith"]

CLASSIFIERS = [
    "Topic :: Software Development :: Libraries",
    "Programming Language:: Python:: 3.9",
]

PACKAGES = find_packages(exclude="tests")


INSTALL_REQUIRES = [
    "virtool-core==0.1.0",
    "click==7.1.2",
    "motor==2.3.0",
    "uvloop==0.14.0",
    "aiohttp==3.7.3",
    "aioredis==1.3.1",
]


ENTRY_POINTS = {
    "console_scripts": [
        "workflow = virtool_workflow_runtime.cli:cli_main",
    ]
}

setup(
    name="virtool_workflow",
    version="0.1.0",
    description="An SDK and runtime for creating Virtool workflows",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/virtool/virtool-workflow",
    author=", ".join(AUTHORS),
    license="MIT",
    platforms="linux",
    packages=PACKAGES,
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.9",
    entry_points=ENTRY_POINTS
)
