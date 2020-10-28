# virtool-workflow

An SDK for developing new Virtool workflows.

[![Build Status](https://cloud.drone.io/api/badges/virtool/virtool-workflow/status.svg)](https://cloud.drone.io/virtool/virtool-workflow)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/1bf01ed0b27040cc92b4ad2380e650d5)](https://www.codacy.com/gh/virtool/virtool-workflow/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=virtool/virtool-workflow&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/1bf01ed0b27040cc92b4ad2380e650d5)](https://www.codacy.com/gh/virtool/virtool-workflow/dashboard?utm_source=github.com&utm_medium=referral&utm_content=virtool/virtool-workflow&utm_campaign=Badge_Coverage)

## Installation

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

A Workflow is defined by an an instance of the `Workflow` class. Startup, step, and 
cleanup functions are added using the `startup`, `step`, and `cleanup` decorator methods 
respectively. 

```python
from virtool_workflow import Workflow

my_workflow = Workflow()

@my_workflow.startup
async def this_will_be_executed_on_startup():
    ...


@my_workflow.step
async def this_is_the_first_step_of_the_workflow():
    ...


@my_workflow.step
async def this_is_the_second_step_of_the_workflow():
    ...


@my_workflow.cleanup
async def this_will_be_executed_last():
    ...
```

All workflow startup, cleanup, and step functions are coroutines. However
any functions added using the `startup`, `step`, or `cleanup` decorators will
be coerced to a coroutine. Thus, the following is also valid.  

```python
@my_workflow.step
def non_async_step_function():
    ...
```

### Workflow Updates

Workflow's are typically long-running. As such updates about the workflow's progress should be sent to 
the user regularly. To facilitate this, the return value (string) from any startup, cleanup, or step 
function will be sent as an update and displayed in the Virtool UI. 

```python
@wf.step
def step_that_sends_an_update():
    ...
    return "Successfully completed a step"

```

Additional updates can be sent using the `context` fixture, described in the **Standard Fixtures** section.

### Workflow Fixtures

Workflow fixtures provide a mechanism for injecting dependencies into workflows. They 
are inspired by and work similarly to [pytest fixtures](https://docs.pytest.org/en/2.8.7/fixture.html).

Fixtures are created using the `virtool_workflow.fixture` decorator. 

```python
from virtool_workflow import fixture

@fixture
def my_workflow_fixture():
    return "my_workflow_fixture"
```

Fixtures are injected into workflow steps based on declared parameter names. When a startup,
cleanup, or step function of a workflow declares a parameter, the appropriate fixture instance will be 
supplied when the function is executed. 

```python
wf = Workflow()

@wf.step
def step(my_workflow_fixture: str):
    print(my_workflow_fixture) # "my_workflow_fixture"
```


#### Fixture Classes

Under the hood, workflow fixtures are subclasses of the `virtool_workflow.WorkflowFixture` class. The `WorkflowFixture`
class is an abstract base class which requires a static method `__fixture__` to be implemented. When the `@fixture` 
decorator is invoked a new subclass is created and the decorated function is used as the `__fixture__` static method. 

```python
from virtool_workflow import WorkflowFixture 

class MyWorkflowFixture(WorkflowFixture, param_names=["my_workflow_fixture", "my_wf_fixture"]):

    @staticmethod
    def __fixture__():
        return "my_workflow_fixture"

```

The fixture will be available within workflows by the names provided in the `param_names` argument. 


### Fixtures Using Other Fixtures

Workflow fixtures can use other fixtures as long as they have been defined before the workflow is executed. To do so
they simply declare a parameter with the same name as the desired fixture.

```python
from virtool_workflow import fixture, Workflow

@fixture
def uses_my_fixture(my_workflow_fixture: str):
    # use my_workflow_fixture
    ...

my_workflow = Workflow()

@my_workflow.step
def step(uses_my_fixture):
    ...

```

Upon execution of the workflow, `my_workflow_fixture` will be instantiated and provided to `uses_my_fixture` as 
an argument. The value returned will then be used as the instance for `uses_my_fixture` which will be passed to the
workflow's step function. 

### Scoping of Workflow Fixtures

Workflow fixtures are scoped to the execution of a particular workflow. This means that any specific fixture
will refer to the exact same instance throughout a workflow's execution. This property allows fixtures to be 
used to pass state between workflow steps. 

```python
from virtool_workflow import fixture, Workflow

@fixture
def mutable_fixture():
    return dict()

wf = Workflow()

@wf.step
def step_1(mutable_fixture):
    mutable_fixture["intermediate value"] = "some workflow state"

@wf.step
def step_2(mutable_fixture):
    print(mutable_fixture["intermediate value"]) # "some workflow state" 
```

This also means that fixtures which were instantiated in-directly (used by other fixtures) will still only be 
instantiated once, even if they are later referred to directly within the workflow. 

### Standard Fixtures

Some standard fixtures are always made available when a workflow is executed. These include; 

| Fixture                          | Description                           | 
|----------------------------------|---------------------------------------|
| results, result                  | The results dictionary                |
| ctx, context, execution_context  | The current WorkflowExecutionContext  |
| wf, workflow                     | The Workflow instance being executed  |

#### The Results Dictionary

The `results` (or `result`) dictionary is used to store the results of the workflow so that they can be provided to 
the end user through the Virtool's UI. It is available within workflows as a fixture. The `results` dictionary is
returned from `virtool_workflow.execute_workflow.execute`. 

```python
    from virtool_workflow import Workflow
    from virtool_workflow.execute_workflow import execute

    wf = Workflow()

    @wf.step
    def add_to_results(results: dict):
        results["result"] = "some result"

    result = await execute(wf) 
    result["result"] # "some result"
    
```

When a workflow is executed as part of a virtool job, the values in the results dictionary will be stored in the 
database and provided to the user. 

#### The Context Fixture
The `context` (or `ctx`, `execution_context`) fixture provides access to the current `WorkflowExecutionContext` instance.
It provides information regarding the state of the workflow's execution, such as the current
step (number) being executed. It can also be used to send additional updates via `context.send_update`.


```python
    @wf.step
    async def send_more_updates(context: WorkflowExecutionContext):
        await context.send_update("Additional update")
        await context.send_update("Another update")
        return "Last update for this step"
```

### Running a Workflow

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
    from virtool_workflow.execute_workflow import execute
    
    my_workflow = Workflow()

    ...

    asyncio.run(execute(my_workflow))
```

## Contributing

### Tests

The testing framework used is [pytest](https://docs.pytest.org/en/stable/).

Run the tests from the root directory:
```shell script
pytest . 
```

The test suite requires MongoDB and Redis to be available. The [test.sh](tests/test.sh)
script will run MongoDB and Redis using Docker for the duration of the tests. Any
arguments will be passed directly to pytest. 

```shell script
./test.sh . 
```


### Documentation

For docstrings, use the [**Sphinx** docstring format](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html).

The packages `sphinx_rtd_theme` and `sphinx_autoapi` are used in rendering the documentation. 

```  shell script
pip install sphinx_rtd_theme sphinx_autoapi
```

#### Markdown for Sphinx

[recommonmark](https://github.com/readthedocs/recommonmark) is used so that Sphinx can 
render documentation from *markdown* files as well as *rst* files. It will need to 
be installed before running `sphinx-build`:

```shell script
pip install recommonmark
```

To use sphinx rst [directives](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html) in a *markdown* file use the 
`eval_rst` [code block](https://recommonmark.readthedocs.io/en/latest/auto_structify.html#embed-restructuredtext)

#### Building the documentation

```shell script
cd sphinx && make html
```
