# Workflow Fixtures

Workflow fixtures are a mechanism for injecting dependencies into Virtool's workflows inspired by pytest's 
[fixtures](https://docs.pytest.org/en/stable/fixture.html). See the [README](../README.md) for basic usage information.

Though full module names will be given for each fixture, all fixtures documented here are imported implicitly by 
`virtool_workflow`'s runtime.

## `results`

The `results` fixture provides a dictionary for storing the results of a workflow. Upon completion of the workflow
the contents of this dictionary will be stored in Virtool's database.

```python
from virtool_workflow import step, hooks
@step
def use_results_dict(results):
    results["result"] = "value"

@hooks.on_result
def print_results(results):
    print(results["value"]) # "value"
```


## `execution`

The `execution` fixture provides a reference to the `virtool_workflow.WorkflowExecution` object responsible for 
executing the current workflow. This object can be used to inquire about the current state of the workflow and to send
additional updates.

```python
@step 
async def use_execution_object(execution):
    await execution.send_update("Additional Update")
    print(execution.current_step) # The current step number of the workflow
    print(execution.progress) # The current percentage of completion as a float
```

## `workflow`

This fixture provides a reference to the `virtool_workflow.Workflow` class which is being executed. 

```python
@step
def use_workflow_reference(workflow):
    ...
```

## `job_args`

`job_args` is a dictionary containing a job's arguments. It's fields will vary depending on the specific 
workflow being executed.

```python
@step
def use_job_args(job_args):
    some_argument = job_args["argument_name"]
    ...
```

## `run_in_executor`

The `run_in_executor` fixture provides a function for executing a `Callable` in the context of a `concurrent.futures
.ThreadPoolExecutor`.

```python
@step
async def run_some_code_in_executor(run_in_executor):
    def run_in_background(...):
        ...

    await run_in_executor(run_in_background, ...)
```

## `run_subprocess`

This fixture provides a function for running shell commands as a subprocess. It ensures that the subprocess will
be killed upon failure, or completion, of the workflow. It also accepts functions for handling stdout, and stderr,
output line-by-line.

```python
async def handle_stdout(line):
    ...

async def handle_stderr(line):
    ...


@step
async def run_a_subprocess(run_subprocess):
    process = await run_subprocess(["some_shell_command"], handle_stdout, handle_stderr)
    ...
```

## Path Fixtures

All path fixtures provide a `pathlib.Path` object and ensure that the directory located by that path exists. Any
temporary directory fixtures, such as `temp_path` and `temp_analysis_path`, are automatically cleared once the workflow
completes, or fails.

### `virtool_workflow.storage.paths.data_path`

This provides the root data path for Virtool. Files under this path may be shared between multiple running workflows
and should be considered read only. Files under the data_path are persisted after the workflow finishes.

```
@step
def sore_some_data(data_path):
    path_to_my_data = data_path/"some_file.txt" 

    with path_to_my_data.open('r') as some_file:
        ...
```

The location of the `data_path` can be configured using the `--data-path-str` CLI argument, or the `VT_DATA_PATH`
environment variable.

### `virtool_workflow.storage.paths.temp_path`

The contents of the `temp_path` are automatically removed when the workflow finishes. Use the `temp_path` to store
data which does not need to persist past the workflow's lifecycle. It is also used to store a local copy, which can
be modified, of shared files stored under the `data_path`.

The location of the temp path can be configured via the `--temp-path-str` CLI argument or the `VT_TEMP_PATH` 
environment variable.

```python
@step
def store_some_temp_data(temp_path):
    (temp_path/"temp.txt").write_text("foobar")
    ...
```

### `virtool_workflow.analysis.paths`

This package defines several path fixtures which depend on the context of the current job.

#### `sample_path`

The sample path locates the sample data being to be analyzed for the current job.

#### `analysis_path`

The analysis path for the current job.

#### `temp_analysis_path`

The path locating the temporary directory which is used for trimming and preparing read data.

#### `index path`

The path locating index data for the current job.

#### `reads_path`

The path where trimmed and quality checked read data is stored for the current analysis.


## Configuration Fixtures

The configuration fixtures, located in `virtool_workflow_runtime.config.configuration`, provide access to the current 
configuration of the workflow runtime. Configuration fixtures each have an associated environment variable and may also
have a default value.

The value of a configuration fixture is determined by the following resolution order:

1. The option provided to the `workflow` CLI
2. The value of the associated environment variable
3. The default value for the fixture

If no default value is set for the fixture, and a value was not otherwise provided, then an exception is raised.

| Fixture     | Description                           | CLI Option | Type | Env | Default | 
|-------------|---------------------------------------|------|-------------|------|-------|
| temp_path_str | The string version of the temp_path. | `--temp-path-str` | `str` | `VT_TEMP_PATH` | `"temp"` |
| data_path_str | The string version of the data_path. | `--data-path-str` | `str` | `VT_DATA_PATH` | `"virtool"` |
| number_of_processes | The number of concurrent processes the workflow is allowed to use. | `--number-of-processes` | `int` | `VT_PROC` | `3` | 
| memory_usage_limit  | The number of GB of ram allocated for the workflow. | `--memory-usage-limit` | `int` | `VT_MEM` | `8` |
| dev_mode | Flag indicating that the runtime is in `dev_mode` (debugging mode). | `--dev-mode` | `bool` | `VT_DEV` | `False` |

### `workflow print-config` and  `workflow create-env-script`

To test that the correct configuration is being loaded you can use `workflow print-config`. It accepts options for 
all of the above fixtures which will take precedent over the environment variable's value. 

```workflow print-config```
> temp_path_str: /home/blakes/w/virtool-workflow/temp \
> data_path_str: /home/blakes/w/virtool-workflow/virtool \
> number_of_processes: 2 \
> memory_usage_limit: 8 \
> dev_mode: False 

The `create-env-script` command will output to `stdout` a shell script which will set the environment variables based
on the given configuration.

```workflow create-env-script --data-path-str="foo" --temp-path-str="bar"```
> export VT_TEMP_PATH=bar \
export VT_DATA_PATH=foo \
export VT_PROC=2 \
export VT_MEM=8 \
export VT_DEV=False

Use it to update the environment variables in the current shell with; 

```source <(workflow create-env-script [OPTIONS])```


```python
from virtool_workflow import step

def use_run_subprocess(run_subprocess):
    async def _stderr_handler(line):
        ...

    async def _stdout_handler(line):
        ...
    
    command = ["some_command", "some_argument"]

    await run_subprocess(command, _stdout_handler, _stderr_handler)
```

`run_subprocess` is imported by the runtime and thus does not need to be imported to be used within a workflow.


## `virtool_workflow.subtractions.subtractions`     

The `subtractions` fixture provides access to the subtraction data 
for a workflow (which is specified by the `job_args["subtraction_id"]` field). It will fetch the appropriate subtraction
data and populate a directory located by the `storage.paths.sample_path` fixture. 

A dataclass `subtractions.Subtraction` is used to contain information about each subtraction. 

```python
@dataclass
class Subtraction:
    """A dataclass representing a subtraction in Virtool."""
    name: str
    nickname: str
    path: Path
    """The Path locating the directory containing the subtraction data."""
    fasta_path: Path
    """The Path locating the compressed FASTA data."""
    bowtie2_index_path: str
    """The prefix of all Paths locating the Bowtie2 index data."""
    count: int
    """The number of chromosomes contained in the subtraction data."""
    gc: Dict[str, float]
    """A dict containing the percentage of occurrence for each nucleotide in the FASTA data."""
```

The `subtractions` fixture yields a `List[Subtraction]`. 


```python
@step
def use_subtractions(subtractions):
    for subtraction in subtractions:
        ...
```


## `virtool_workflow.analysis.read_prep.reads`

The prepared read data for an analysis workflow is accessed using the `virtool_workflow.analysis.read_prep.reads` fixture.
It yields an instance of the `virtool_workflow.analysis.reads.Reads` dataclass. 

```python
@dataclass
class Reads:
    """Dataclass representing prepared reads for an analysis workflow."""
    paired: bool
    """A boolean indicating that the read data is paired."""
    min_length: int
    """The minimum sequence length."""
    max_length: int
    """The maximum sequence length."""
    count: int
    """The number of sequences in the sample."""
    paths: Iterable[Path]
    """The paths locating the trimmed read data."""
```

Using the `reads` fixture within a workflow triggers the read preparation steps to be run. Those steps will be completed 
before the fixture returns. This replaces what would have previously been done using the `make_analysis_directory` and 
`prepare_reads` functions in `virtool.jobs.analysis`. 

Additionally, if there is a cache of the trimmed reads available it will be used and the read
preparation will be avoided. If no cache is available a new one will be made once the read prep completes. 


```python
from virtool_workflow import step
from virtool_workflow.analysis.reads import Reads


@step
def use_reads(reads: Reads):
    if reads.paired:
        read1, read2 = reads.paths
    else:
        read, = reads.paths
    ... # Do something with read data
```

The raw sample data to be prepared is expected to be present under the `sample_path`.

### `virtool_workflow.analysis.read_prep.unprepared_reads`

This fixture returns the same `virtool_workflow.analysis.reads.Reads` object as the `reads` fixture, but does not 
trigger the read preparation steps

### `virtool_workflow.analysis.read_prep.parsed_fastqc`

`parsed_fastqc` provides access to the `fastqc` data which is produced as part of the read preparation. If used after
the `reads` fixture it will return immediately, since it is used by the `reads` fixture. 

## Writing Tests For Fixtures And Functions Which Use Them


### Direct Instantiation

All fixtures can be called as functions and directly provided their parameters as they are declared. This can be useful
for testing that a fixture provides the correct value. 

```python
import virtool_workflow

@virtool_workflow.fixture
async def my_fixture(some_other_fixture):
    ...


def test_my_fixture_without_my_other_fixture():
    mock_value_for_my_other_fixture = ...
    result = await my_fixture(mock_value_for_my_other_fixture)
```

### Create An Empty WorkflowFixtureScope

To test fixtures or functions that depend on many other fixtures it is best to create a fresh 
`virtool_workflow.fixtures.scope.WorkflowFixtureScope`. 

```python
import virtool_workflow
from virtool_workflow.fixtures.scope import WorkflowFixtureScope

@virtool_workflow.fixture
def my_fixture(...):
    ...

def function_using_fixture(my_fixture, ...):
    ...


def test_fixture_and_function():
    with WorkflowFixtureScope as scope:
        await scope.instantiate(my_fixture)
        
        bound_function = await scope.bind(function_using_fixture)
        bound_function()
        ...
```

To inject specific instances into the scope for testing purposes you can simply use the `WorkflowFixtureScope` as a dict.

```python
def test_fixture_and_function_with_mocks():
    with WorkflowFixtureScope as scope:
        scope["mocked_fixture"] = "mock_value"
        await scope.instantiate(my_fixture)
        
        bound_function = await scope.bind(function_using_fixture)
        bound_function()
        ...
```

### The `runtime` pytest fixture.

The `virtool_workflow_runtime.test_utils` package provides utilities for testing Virtool workflows. The 
`runtime` fixture provides a harness for running workflows and functions which use
runtime fixtures.

```python
from virtool_workflow_runtime.test_utils import runtime
from virtool_workflow_runtime.runtime import execute

from ... import function_to_test
from ... import workflow_to_test

async def test_function(runtime):

    result = await runtime.execute_function(function_to_test)
    assert ...

async def test_workflow(runtime):
    runtime.scope["job_args"] = {...}
    result = await runtime.execute(workflow_to_test)


async def test_workflow_and_hooks(runtime):
    result = await execute(workflow_to_test, runtime)
```

### Using A Pytest Fixture For The WorkflowFixtureScope

Often when writing tests there are many different fixtures which need to be mocked, including the built-in fixtures 
provided by the runtime such as the `job_args`. It is helpful to use a pytest fixture to perform the initialization
which is common between different tests.

```python
import pytest
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from ... import function_to_test

@pytest.yield_fixture()
def workflow_fixtures():
    with WorkflowFixtureScope as scope:
        scope["job_args"] = {...}
        scope["job_id"] = "1"
        ...
        yield scope


def test_using_fixtures(workflow_fixtures):
    bound = await workflow_fixtures.bind(function_to_test)
    ret = bound()

    assert ...
```