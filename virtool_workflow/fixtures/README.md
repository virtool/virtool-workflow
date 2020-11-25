# Workflow Fixtures

## Fixtures Provided By The Runtime

The fixtures which are automatically imported by the runtime for any type of workflow are: 

| Fixture     | Description                           | Type |
|-------------|---------------------------------------|------|
| results     | The results dictionary                | `dict` |
| execution   | The current WorkflowExecution         | `virtool_workflow.WorkflowExecution` |
| workflow    | The Workflow instance being executed  | `virtool_workflow.Workflow` |
| data_path   | The root path for data                | `pathlib.Path` |
| temp_path   | The root path for temporary files     |`pathlib.Path` |
| job_id      | The ID of the current job       | `str` |
| job_document| The database document (dict) for the current job | `dict` |
| job_args    | The arguments provided for the job from the front end application. | `dict` |
| run_in_executor | A function which runs functions in a `concurrent.futures.ThreadPoolExecutor` | `Callable[[Callable, Iterable[Any], dict], Coroutine` |
| scope       | The `WorkflowFixtureScope` object being used to bind fixtures for this workflow | `virtool_workflow.fixtures.scope.WorkflowFixtureScope` |

The `job_id`, `job_document`, and `job_args` fixtures are not available when running a workflow using `workflow run-local`.



