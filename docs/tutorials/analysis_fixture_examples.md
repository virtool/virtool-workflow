# Example Usage of Analysis Fixtures

This guide contains examples showcasing how to use fixtures from `virtool_workflow.analysis` from within
A workflow, along with explanations of any non-obvious work they perform. 

The fixtures in question are:

- `virtool_workflow.analysis.analysis_info.AnalysisInfo`
- `virtool_workflow.analysis.analysis_info.AnalysisArguments`
- Those fixtures such as `virtool_workflow.analysis_info.paired` which 
  delegate to `virtool_workflow.analysis.analysis_info.AnalysisArguments`
- Fixtures relating to caching and read preparation. 
- Fixtures relating to fastqc.

## The AnalysisArguments Fixture

The `AnalysisArgumnents` fixture, identified in workflows by `analysis_args` is a dataclass containing 
all information used in analysis workflows which is dependent/determined from the information in the 
various database documents associated to the current analysis job. 

### Fixtures For The Individual Properties of AnalysisArguments

Each property of AnalysisArguments (excluding the `reads_path`) has a fixture of the same name which refers to 
it directly. These fixtures delegate to the `AnalysisArguments` fixture, so use of any of them will instantiate 
the `AnalysisArguments`.

```python
@step
def using_analysis_args(analysis_args: AnalysisArguments):
    print(id(analysis_args.index_path))


@step
def using_index_path(index_path: Path):
    print(id(index_path))
```

Here `analysis_args.index_path` in `using_analysis_args` is the exact same instance as `index_path` in `using_index_path`.

## Read Preparation And The `reads_path`

All analysis workflows have the initial step of trimming the raw read data (using `skewer`) and 
running `fastqc`. The `virtool_workflow.analysis.read_paths.reads_path` fixture triggers the read preparation
and provides access to the location of the prepared reads once the trimming and other preparation steps have been 
completed.

```python
from virtool_workflow import step
from virtool_workflow.analysis.read_paths import reads_path

@step
def use_reads_path(reads_path):
    with (reads_path/"reads_1.fq.gz").open("r") as read_data:
        # do something with read_data
        ...
```


