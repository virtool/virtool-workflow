# Virtool Workflow

![Tests](https://github.com/virtool/virtool-workflow/workflows/Tests/badge.svg?branch=master)
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

- [Documentation](https://workflow.virtool.ca)
- [Website](https://www.virtool.ca/)

## Contributing

### Commits

All commits must follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0) specification.

These standardized commit messages are used to automatically publish releases using [`semantic-release`](https://semantic-release.gitbook.io/semantic-release)
after commits are merged to `main` from successful PRs.

**Example**

```text
feat: add API support for assigning labels to existing samples
```

Descriptive bodies and footers are required where necessary to describe the impact of the commit. Use bullets where appropriate.

Additional Requirements

1. **Write in the imperative**. For example, _"fix bug"_, not _"fixed bug"_ or _"fixes bug"_.
2. **Don't refer to issues or code reviews**. For example, don't write something like this: _"make style changes requested in review"_.
   Instead, _"update styles to improve accessibility"_.
3. **Commits are not your personal journal**. For example, don't write something like this: _"got server running again"_
   or _"oops. fixed my code smell"_.

From Tim Pope: [A Note About Git Commit Messages](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)

### Poetry

Dependencies & virtual environments are managed with [Poetry](https://python-poetry.org/ "Poetry")

To install `poetry`:

```sh
sudo pip install poetry
```

To install dependencies, and the `virtool-workflow` package, into a virtual environment:

```sh
git clone https://github.com/virtool/virtool-workflow
cd virtool-workflow

poetry install
```

To run commands in the virtual environment:

```sh
poetry run <<command>>
```

### Tests

[Pytest](https://docs.pytest.org/en/7.1.x/ "Pytest") is used to implement unit
and integration tests.

A pytest plugin,
[pytest-docker-compose](https://github.com/pytest-docker-compose/pytest-docker-compose)
handles starting and stopping any required external services for integration
tests. [docker-compose](https://docs.docker.com/compose/) will need to be
installed on your system for this to work. It might also be necessary to setup a
`docker` user group on your system, so you can [use docker without
sudo](https://linoxide.com/use-docker-without-sudo-ubuntu/).

`virtool-workflow` depends on some external bioinformatics tools such as [Bowtie
2](http://bowtie-bio.sourceforge.net/bowtie2/index.shtml),
[FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/), and
[Skewer](https://github.com/relipmoc/skewer). Installation of these tools can be
somewhat involved, so it's best to run the test suite using `docker`. The
[virtool/workflow-tools](https://github.com/virtool/workflow-tools) image
provides a base with all of the external dependencies pre-installed.

[./tests/docker-compose.yml](./tests/docker-compose.yml) will run the test suite
inside a container based on
[virtool/workflow-tools](https://github.com/virtool/workflow-tools) and mount
the local docker socket so that `pytest`, running inside the container, can
manage the other services required by the integration tests.

To run the entire test suite:

```sh
cd tests
docker-compose up --exit-code-from pytest
```

To run a subset of the tests, `tests/integration` only for example:

```sh
cd tests
TEST_PATH=tests/integration docker-compose up --exit-code-from pytest
```

:warning: The `TEST_PATH` is a relative path from the repository root, not the `tests` directory.
