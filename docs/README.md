# Virtool Workflow

![Tests](https://github.com/virtool/virtool-workflow/workflows/Tests/badge.svg?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/1bf01ed0b27040cc92b4ad2380e650d5)](https://www.codacy.com/gh/virtool/virtool-workflow/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=virtool/virtool-workflow&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/1bf01ed0b27040cc92b4ad2380e650d5)](https://www.codacy.com/gh/virtool/virtool-workflow/dashboard?utm_source=github.com&utm_medium=referral&utm_content=virtool/virtool-workflow&utm_campaign=Badge_Coverage)



<p>
  <a href="#installation">Installation</a> •
  <a href="#quickstart">Quickstart</a> •
  <a href="#links">Links</a> •
  <a href="#contributing">Contributing</a> 
</p>


A framework for developing bioinformatic workflows in Python.


## Installation

### Latest Stable Release

```shell script
pip install virtool-workflow
```

### Latest Development Changes

```shell script
pip install git+https://github.com/virtool/virtool-workflow.git
```

## Quickstart

### Workflow Definition

Workflow steps are defined using the startup, step, and 
cleanup functions are added using the `startup`, `step`, and `cleanup` decorator methods 
respectively. 


```python
from virtool_workflow import startup, step, cleanup

@startup
def startup_function():
    ...

@step 
def step_function():
    ...

@step
def step_function_2():
    ...

@cleanup
def cleanup_function():
    ...
```

Within their own sets, the `step`, `startup`, and `cleanup` functions will be executed in **definition order**. As such
`step_function_2()` in the above example will be executed after `step_function()`.

All workflow startup, cleanup, and step functions are coroutines. However
any functions added using the `startup`, `step`, or `cleanup` decorators will
be coerced to a coroutine. Thus, the following is also valid.  

```python
@step
def non_async_step_function():
    ...
```

### Workflow Fixtures

Inspired by [pytest fixtures](https://docs.pytest.org/en/2.8.7/fixture.html),  workflow fixtures provide access to dependencies via function parameters.

```python
from virtool_workflow import fixture

@fixture
def package_name():
    return "virtool_workflow"
```

The above defines a fixture `package_name` with a value of `"virtool_workflow"`. This fixture can then be used freely 
in workflow steps by taking *package_name* as a parameter.
```python
@step
def step(package_name: str):
    ...
```


### Fixtures Using Other Fixtures

Fixtures may depend on other fixtures. Here is an example of how two fixtures (`package_name` and `package_version`) can be composed.

```python

@fixture
def pinned_package_name(package_name: str, package_version: str):
    return f"{package_name}=={package_version}"
```

### Sharing Data Between Steps

A fixture, once instantiated, will persist through a workflow's entire execution. This means that mutable objects,  such as dictionaries, can be used to pass information between the steps of a workflow.

```python
from virtool_workflow import fixture, step

@fixture
def mutable_fixture():
    return dict()

@step
def step_1(mutable_fixture):
    mutable_fixture["intermediate value"] = "some workflow state"

@step
def step_2(mutable_fixture):
    print(mutable_fixture["intermediate value"]) # "some workflow state" 
```

## Links

* [API Docs](https://workflow.virtool.ca/)
* [PyPi Package](https://pypi.org/project/virtool-workflow/)
* [Virtool Website](https://www.virtool.ca/)

## Contributing

### Virtual Environment

---

[Poetry](https://python-poetry.org/) is used to manage the dependencies and virtual environment.

#### Install Dependencies

```shell script
pip install poetry
poetry install
```

#### Run Commands In The Virtual Environment

```shell script
poetry run <command>
```

### Unit Tests

---

```shell script
cd tests
docker-compose up --build --exit-code-from pytest
```

### API Documentation

---

For doc-strings, use the [**Sphinx** docstring format](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html).

#### Build

```shell script
(cd docs && ./build-docs.sh)
```

#### Live Preview

```
pip install sphinx-autobuild
sphinx-autobuild sphinx sphinx/_docs/html
```

