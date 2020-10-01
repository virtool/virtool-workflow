from setuptools import setup, find_packages
from pathlib import Path

AUTHORS = ["Ian Boyes", "Blake Smith"]

CLASSIFIERS = [
    "Topic :: Software Development :: Libraries",
    "Programming Language:: Python:: 3.6",
]

PACKAGES = find_packages(exclude="tests")

INSTALL_REQUIRES = [
    "git+https://github.com/virtool/virtool-core",
    "click",
]

SETUP_REQUIRES = [
    "pytest",
    "setuptools>=40.0",
]


ENTRY_POINTS = {
    "console_scripts": [
        "virtool_worflow = virtool_workflow._runtime:cli_main",
    ]
}

setup(
    name="virtool_workflow",
    description="An SDK and runtime for creating Virtool workflows",
    long_description=Path("README.md").read_text(),
    url="https://github.com/virtool/virtool-workflow",
    author=", ".join(AUTHORS),
    lisense="MIT",
    platforms="linux",
    packages=PACKAGES,
    install_requires=INSTALL_REQUIRES,
    setup_requries=SETUP_REQUIRES,
    python_requires=">=3.6",
    package_dir="virtool_workflow",
)