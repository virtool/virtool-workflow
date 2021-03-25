# A Base Image For Virtool Workflows

## Usage

```dockerfile
FROM virtool/workflow

COPY my_workflow.py workflow.py
COPY my_fixtures.py fixtures.py
```

The `virtool_workflow_standalone` Dockerfile sets the ENTRYPOINT command to;

```
workflow run
```

As such any CLI arguments (see `workflow run --help`) can be passed along when running the container.

