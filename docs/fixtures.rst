Fixtures
********

Workflow
========

Basic fixtures for using the workflow environment.

:func:`.job_id`
---------------

The ID of the Virtool job for the running workflow.


:func:`.work_path`
------------------

The path to a temporary directory where all files for the running workflow should be stored.

Returns a :class:`~pathlib.Path` object.

.. code-block:: python

    @step
    async def prepare(work_path: Path):
        work_path.mkdir("output")

:func:`.proc`
-------------

The maximum number of processors that the workflow can use at once.

:func:`.mem`
------------

The maximum memory (GB) the the workflow can use at once.

Sample Data
===========

:func:`.sample`
---------------

The `sample <https://www.virtool.ca/docs/manual/guide/samples>`_ associated with the workflow run.

Returns a :class:`.Sample` object.

.. code-block:: python

    @step
    async def align(sample):
        pass

:func:`.paired`
---------------


Indicates whether the sample associated with the workflow run contains paired data.

.. code-block:: python

    @step
    async def align(paired: bool):
        if paired:
            align_paired_data()
        else:
            align_unpaired_data()


:func:`.library_type`
---------------------

The library type of the sample associated with the workflow run.

One of ``"normal"``, ``"srna"``, or ``"amplicon"``.

.. code-block:: python

    @step
    def deduplicate(library_type: LibraryType):
        if library_type == "amplicon":
            deduplicate_amplicon_reads()


Non-Sample Data
===============

Fixtures provide access to Virtool's non-sample data.

Non-sample data includes references and indexes, profile hidden Markov models (HMMs), and subtractions.

:func:`.hmms`
-------------

Provides all HMM annotations and the `profiles.hmm` file.

Returns an :class:`.HMMs` object.

.. code-block:: python

    @step
    def hmmscan(hmms):



:func:`.indexes`
----------------

The Virtool `reference indexes <https://www.virtool.ca/docs/manual/guide/indexes>`_ available for the current workflow.

Returns a :class:`list` of :class:`.Index` objects.

:func:`.subtractions`
---------------------

The Virtool `subtractions <https://www.virtool.ca/docs/manual/guide/subtraction>`_ that were set when the analysis workflow was started.

Returns a :class:`list` of :class:`.Subtraction` objects.
