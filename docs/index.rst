Virtool Workflow
============================================

A framework for developing bioinformatic workflows for Virtool.

Virtool Workflow uses decorators to define steps in the workflow.

.. code-block:: python

   from virtool_workflow import startup, step, cleanup

   @startup
   def startup_function():
       ...

   @step
   def step_1():
       ...

   @step
   def step_2():
       ...

   @cleanup
   def cleanup_function():
       ...


.. toctree::
    :hidden:

    install.rst
    quickstart.rst
    fixtures.rst
    hooks.rst
    reference.rst
    contributing.rst
