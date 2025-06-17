# Virtool Workflow

[![CI](https://github.com/virtool/virtool-workflow/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/virtool/virtool-workflow/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/virtool-workflow.svg)](https://badge.fury.io/py/virtool-workflow)

A framework for developing bioinformatic workflows in Python.

```python
from virtool_workflow import step


@step
def step_function():
    ...


@step
def step_function_2():
    ...
```

## Contributing

### Commits

We require specific commit formatting. Any commit that does not follow the guidelines
will be squashed at our discretion.

Read our [commit and release](https://dev.virtool.ca/en/latest/commits_releases.html)
documentation for more information.

### Tests

Run tests with:

```shell
# Bring up Redis and the test container.
docker compose up -d

# Run tests in the test container.
docker compose exec test poetry run pytest
```

Run specific tests like:

```shell
docker compose exec test poetry run pytest tests/test_status.py
```
