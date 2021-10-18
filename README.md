# Virtool Workflow

![Tests](https://github.com/virtool/virtool-workflow/workflows/Tests/badge.svg?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/1bf01ed0b27040cc92b4ad2380e650d5)](https://www.codacy.com/gh/virtool/virtool-workflow/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=virtool/virtool-workflow&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/1bf01ed0b27040cc92b4ad2380e650d5)](https://www.codacy.com/gh/virtool/virtool-workflow/dashboard?utm_source=github.com&utm_medium=referral&utm_content=virtool/virtool-workflow&utm_campaign=Badge_Coverage)

A framework for developing bioinformatic workflows in Python.

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

* [Documentation](https://workflow.virtool.ca)
* [Virtool Website](https://www.virtool.ca/)
* [PyPI Package](https://pypi.org/project/virtool-workflow/)

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
