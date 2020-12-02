# Workflow Fixtures

## Build-in Fixtures

The fixtures which are automatically imported by the runtime for any type of workflow are: 

| Fixture     | Description                           | Type |
|-------------|---------------------------------------|------|
| results     | The results dictionary                | `dict` |
| execution   | The current WorkflowExecution         | `virtool_workflow.WorkflowExecution` |
| workflow    | The Workflow instance being executed  | `virtool_workflow.Workflow` |
| data_path   | The root path for data                | `pathlib.Path` |
| temp_path   | The root path for temporary files     |`pathlib.Path` |
| proc        | The number of allowable processes for the current job  | `int` |
| mem         | The amount of RAM available for the current job, in GB | `int` |
| job_id      | The ID of the current job       | `str` |
| job_document| The database document (dict) for the current job | `dict` |
| job_args    | The arguments provided for the job from the front end application. | `dict` |
| run_in_executor | A function which runs functions in a `concurrent.futures.ThreadPoolExecutor` | `Callable[[Callable, Iterable[Any], dict], Coroutine` |
| scope       | The `WorkflowFixtureScope` object being used to bind fixtures for this workflow | `virtool_workflow.fixtures.scope.WorkflowFixtureScope` |

The `job_id`, `job_document`, and `job_args` fixtures are not available when running a workflow using `workflow run-local`.

## Configuration

The configuration fixtures are loaded in by the CLI when the `worklflow run` or `workflow run-local` commands are used. 
Each of them corresponds to a command line argument provided by the CLI. Each also has an environment variable whose value
will be used if there is no argument provided, and optionally a default value that will be used if the environment
variable is not set. 

These are available automatically and do not need to be imported. 

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

## `virtool_workflow.execution.run_subprocess.run_subprocess`

`virtool_workflow.execution.run_subprocess.run_subprocess` fixture provides a function for running shell commands in a
subprocess. The signature of that function is as follows;

```python
 async def run_subprocess(
            command: List[str],
            stdout_handler: Optional[Callable[[str], Coroutine]] = None,
            stderr_handler: Optional[Callable[[str], Coroutine]] = None,
            env: Optional[dict] = None,
            cwd: Optional[str] = None,
            wait: bool = True,
    ):
        """
        Run a command as a subprocess and handle stdin and stderr output line-by-line.

        :param command: The command to run as a subprocess.
        :param stdout_handler: A function to handle stdout lines.
        :param stderr_handler: A function to handle stderr lines.
        :param env: Environment variables to set for the subprocess.
        :param cwd: Current working directory for the subprocess.
        :param wait: Flag indicating to wait for the subprocess to finish before returning.

        :return: A asyncio.subprocess.Process object.
        """
        ...
```

`run_subprocess` also ensures that the process will be terminated in the event of a failure. 

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

## Storage

The `virtool_workflow.storage` package provides the following fixtures; 

### `virtool_workflow.storage.paths.data_path`

The data path is provided by `virtool_workflow.storage.paths.data_path`. The
`data_path` fixture gives a `pathlib.Path` object which is created using the
`data_path_str` fixture. The directory located by the `data_path` will be created 
if it does not exist. 

```python
from virtool_workflow import step
from virtool_workflow.storage.paths import data_path

@step
def use_data_path(data_path, data_path_str):
    print(data_path.exists()) # True
    print(str(data_path) == data_path_str) # True
 ```

### `virtool_workflow.storage.paths.temp_path`

The `virtool_workflow.storage.paths.temp_path` fixture initializes a 
temporary directory at the path of `temp_path_str` and returns a `pathlib.Path`
object locating it.  

Once the workflow finishes executing the `temp_path` directory and it's contents
will be destroyed. 

```python
from virtool_workflow import step
from virtool_workflow.storage.paths import temp_path

@step
def use_temp_path(temp_path):
    print(temp_path.exists()) # True
 ```


### `virtool_workflow.storage.paths.cache_path`

`virtool_workflow.storage.paths.cache_path` provides a `pathlib.Path` object locating a directory
containing any cached read data. When read prep steps for an analysis workflow are performed a cache is 
created to be used in the event that the workflow fails and is restarted. 

The `cache_path` is located under the `data_path` and is not cleared when 
the workflow finishes. 

```python
from virtool_workflow import step
from virtool_workflow.storage.paths import cache_path

@step
def use_temp_path(cache_path):
    print(cache_path.exists()) # True
 ```

### `virtool_workflow.storage.paths.subtraction_data_path` and `virtool_workflow.storage.paths.subtraction_path`

`virtool_workflow.storage.paths.subtraction_data_path` locates the subtraction data. In
contrast, `virtool_workflow.storage.paths.subtraction_path` locates the temporary directory 
where a copy of the subtraction data required by a workflow will be stored when the 
`subtractions` fixture is used. 

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
from typing import List
from virtool_workflow import step
from virtool_workflow.subtractions import subtractions, Subtraction

@step
def use_subtractions(subtractions: List[Subtraction]):
    for subtraction in subtractions:
        ...
```


## `virtool_workflow.analysis.analysis_info.AnalysisArguments`

The `analysis_args` (virtool_workflow.analysis.analysis_info.AnalysisArguments) fixture provides access to various 
parameters used within analysis workflows which were provided by the frontend application via the database. 
It provides an instance of the `virtool_workflow.analysis.analysis_info.AnalysisArguments` dataclass.

```python
@dataclass(frozen=True)
class AnalysisArguments(WorkflowFixture, param_name="analysis_args"):
    """Dataclass containing standard arguments required for Virtool analysis workflows."""
    path: Path
    sample_path: Path
    index_path: Path
    reads_path: Path
    read_paths: utils.ReadPaths
    subtraction_path: Path
    raw_path: Path
    temp_cache_path: Path
    temp_analysis_path: Path
    paired: bool
    read_count: int
    sample_read_length: int
    library_type: LibraryType
    sample: Dict[str, Any]
    analysis: Dict[str, Any]
    sample_id: str
    analysis_id: str
    ref_id: str
    index_id: str
```

Each field of the dataclass is also available as a fixture on it's own. For example, the `virtool_workflow.analysis.analsysis_info.sample`
fixture has exactly the same value as `analysis_args.sample`.

```python
from virtool_workflow import step
from virtool_workflow.analysis.analysis_info import AnalysisArguments, sample

@step
def use_analysis_args(analysis_args: AnalysisArguments, sample: dict):
    assert analysis_args.sample == sample # True

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
    paths: ReadPaths
    """The paths locating the trimmed read data."""
```

Using the `reads` fixture within a workflow triggers the read preparation steps to be run. Those steps will be completed 
before the fixture returns. This replaces what would have previously been done using the `make_analysis_directory` and 
`prepare_reads` functions in `virtool.jobs.analysis`. 

Additionally, if there is a cache of the trimmed reads available under the `cache_path` that will be used and the read
preparation will be avoided. If no cache is available a new one will be made once the read prep completes. 


```python
from virtool_workflow import step
from virtool_workflow.analysis.read_prep import reads
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