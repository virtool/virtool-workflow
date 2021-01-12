# virtool-workflow

A framework for developing new Virtool workflows.

![Tests](https://github.com/virtool/virtool-workflow/workflows/Tests/badge.svg?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/1bf01ed0b27040cc92b4ad2380e650d5)](https://www.codacy.com/gh/virtool/virtool-workflow/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=virtool/virtool-workflow&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/1bf01ed0b27040cc92b4ad2380e650d5)](https://www.codacy.com/gh/virtool/virtool-workflow/dashboard?utm_source=github.com&utm_medium=referral&utm_content=virtool/virtool-workflow&utm_campaign=Badge_Coverage)

## Installation

Install from PyPi using;

```shell script
pip install virtool-workflow
```

Or install from source;

```shell script
git clone https://github.com/virtool/virtool-workflow.git
pip install .

#  Or

pip install git+https://github.com/virtool/virtool-workflow.git
```

This will install both the `virtool_workflow` library and the `workflow` command line utility.

## Quickstart

A Workflow is comprised of 

1. A set of setup functions to execute on before the main steps.
2. A set of functions (steps) to be executed. 
3. A set of cleanup functions to be executed once the steps are complete.

### Basic Workflow Definition

A Workflow is defined by an an instance of the [Workflow](#) class. Startup, step, and 
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

### Workflow Updates

Workflow's are typically long-running. As such updates about the workflow's progress should be sent to 
the user regularly. To facilitate this, the return value (string) from any startup, cleanup, or step 
function will be sent as an update and displayed in the Virtool UI. 

```python
@step
def step_that_sends_an_update():
    ...
    return "Successfully completed a step"

```

Additional updates can be sent using the [execution](#) fixture, described in the **Standard Fixtures** section.

### Workflow Fixtures

Workflow fixtures provide a mechanism for injecting dependencies into workflows. They 
are inspired by and work similarly to [pytest fixtures](https://docs.pytest.org/en/2.8.7/fixture.html).

Fixtures utilize the parameter names of a function as identifiers of a particular instance to supply 
as an argument.

Fixtures are created using the [virtool_workflow.fixture](#) decorator on a factory function which produces 
the instance to be injected.

```python
from virtool_workflow import fixture

@fixture
def my_workflow_fixture():
    return "my_workflow_fixture"
```

The above defines a fixture with a value of `"my_workflow_fixture"`.

When a startup, cleanup, or step function of a workflow declares a parameter, the appropriate fixture instance will be 
supplied when the function is executed, as long as the fixture is defined within the 
current scope (or global/module scope)

```python
@step
def step(my_workflow_fixture: str):
    print(my_workflow_fixture) # "my_workflow_fixture"
```


#### Fixture Classes

Under the hood, workflow fixtures are subclasses of the [virtool_workflow.WorkflowFixture](#) class. The `WorkflowFixture`
class is an abstract base class which requires a static method `__fixture__` to be implemented. When the `@fixture` 
decorator is invoked a new subclass is created and the decorated function is used as the `__fixture__` static method. 

```python
from virtool_workflow import WorkflowFixture 

class MyWorkflowFixture(WorkflowFixture, param_name="my_workflow_fixture"):

    @staticmethod
    def __fixture__():
        return "my_workflow_fixture"

```

The fixture will be available within workflows by the name specified by `param_name`.


### Fixtures Using Other Fixtures

Workflow fixtures can use other fixtures as long as they have been defined before the workflow is executed. To do so
they simply declare a parameter with the same name as the desired fixture.

```python
from virtool_workflow import fixture, step

@fixture
def uses_my_fixture(my_workflow_fixture: str):
    # use my_workflow_fixture
    ...

@step
def step(uses_my_fixture):
    ...

```

Upon execution of the workflow, `my_workflow_fixture` will be instantiated and provided to `uses_my_fixture` as 
an argument. The value returned will then be used as the instance for `uses_my_fixture` which will be passed to the
workflow's step function. 

### Mutable Fixtures as a Means of Sharing Data Between Workflow Steps

Workflow fixtures are scoped to the execution of a particular workflow. This means that any specific fixture
will refer to the exact same instance throughout a workflow's execution. This property allows fixtures to be 
used to pass state between workflow steps. 

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

This also means that fixtures which were instantiated in-directly (used by other fixtures) will still only be 
instantiated once, even if they are later referred to directly within the workflow. 

For more details about fixture scope and binding see the [API docs](#).

### Standard Fixtures

Some standard fixtures are always made available when a workflow is executed. These include; 

| Fixture     | Description                           | 
|-------------|---------------------------------------|
| results     | The results dictionary                |
| execution   | The current WorkflowExecution         |
| workflow    | The Workflow instance being executed  |

A more complete list of available fixtures can be found [here](virtool_workflow/fixtures/README.md)

#### The Results Dictionary

The `results` dictionary is used to store the results of the workflow so that they can be provided to 
the end user through the Virtool's UI. It is available within workflows as a fixture. The `results` dictionary is
returned from `virtool_workflow.execute_workflow.execute`. 

```python
    from virtool_workflow import step, hooks

    @step
    def add_to_results(results: dict):
        results["result"] = "some result"


    @hooks.on_result
    def print_result(workflow, results):
        print(results["result"]) # prints "some_result"
```

When a workflow is executed as part of a virtool job, the values in the results dictionary will be stored in the 
database and provided to the user. 

#### The Context/Execution Fixture
The `execution` fixture provides access to the current `WorkflowExecution` instance.
It provides information regarding the state of the workflow's execution, such as the current
step (number) being executed. It can also be used to send additional updates via `.send_update`.


```python
    @step
    async def send_more_updates(execution: WorkflowExecution):
        await execution.send_update("Additional update")
        await execution.send_update("Another update")
        return "Last update for this step"
```

### Running a Workflow Outside of the Runtime

Assuming your workflow is defined in `workflow.py` in the current working directory, 
you can execute it using the `workflow` command line utility. 

```shell script
    workflow run_local 
    # or for files other than workflow.py
    workflow run_local -f "script_with_a_workflow.py"
```

The `workflow` utility simply looks for an instance of `Workflow` within `workflow.py` 
(or the provided file).

A workflow can also be executed from python using `virtool_workflow.execute_workflow.execute`.

```python
    import asyncio
    from virtool_workflow import Workflow
    from virtool_workflow.execution.execute_workflow import execute
    
    my_workflow = Workflow()

    ...

    asyncio.run(execute(my_workflow))
```


### Responding to Runtime Events

The workflow runtime provides several hooks into it's lifecycle. These
can be accessed via the [virtool_workflow.hooks](#) module. 

Here is an example using the `on_result` hook, which is triggered after all 
cleanup steps have been completed.

```python
from virtool_workflow import hooks, Workflow
from typing import Dict, Any

@hooks.on_result
def respond_to_workflow_result(workflow: Workflow, results: Dict[str, Any]):
    ...
```

The function `respond_to_workflow_result` will be called once the workflow result is available. The
`on_result` hook expects two parameters, but all hooks can also accept functions without parameters.

```python
@hooks.on_result
async def respond_to_result_but_without_parameters():
    ...
```

The callback functions provided for a hook can be either async functions or standard 
functions. Any standard function provided will be wrapped into an async function.

## Contributing

### Tests

The testing framework used is [pytest](https://docs.pytest.org/en/stable/).

Run the tests using tox:
```shell script
tox
```

The test suite requires MongoDB and Redis to be available. The [test.sh](tests/test.sh)
script will run MongoDB and Redis using Docker for the duration of the tests. Any
arguments will be passed directly to pytest. 

```shell script
./tests/test.sh 
```


### Documentation

For docstrings, use the [**Sphinx** docstring format](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html).

#### pydoc-markdown

[pydoc-markdown](https://pydoc-markdown.readthedocs.io/en/latest/) is used to generate python API documentation
in markdown format. 

```shell script
pip install pydoc-markdown
```

##### Building And Viewing the API Documentation

From the repository root directory run;

```shell script
pydoc-markdown --server --open
```

This will open a browser window showing the rendered documentation.
The source markdown files are available under `build/content/docs`. The 
page will reload the page automatically when any of the source files change.
