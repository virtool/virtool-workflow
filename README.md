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
