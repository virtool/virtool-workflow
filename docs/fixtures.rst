########
Fixtures
########

Fixtures are functions whose return values can be requested and provided to other functions. Their implementation in
Virtool Workflow was inspired by `pytest <https://docs.pytest.org/en/2.8.7/fixture.html>`_.

:ref:`Built-in fixtures <Built-in Fixtures>` are used in Virtool to allow controlled access to Virtool application data
required for the workflow to run. Users can also create their own fixtures to share data between steps or to reuse code.

Fixtures are requested in a by including the fixture name as an argument in the requesting function. For example:

.. code-block:: python

    from virtool_workflow import fixture, step

    @fixture
    def sequence():
        return "ATGGACAGGTAGGCACAACACA"

    @step
    async def step_1(sequence):
        with open("genome.fa", "r") as f:
            detected = sequence in f.read():


Built-in Fixtures
=================

Virtool Workflow includes many built-in fixtures for interacting with the workflow environment and accessing Virtool
application data.

Configuration
-------------

Basic fixtures for using the workflow environment.

:func:`.job_id`
^^^^^^^^^^^^^^^

The ID of the Virtool job for the running workflow.


:func:`.work_path`
^^^^^^^^^^^^^^^^^^

The path to a temporary directory where all files for the running workflow should be stored.

Returns a :class:`~pathlib.Path` object.

.. code-block:: python

    @step
    async def prepare(work_path: Path):
        work_path.mkdir("output")

:func:`.proc`
^^^^^^^^^^^^^

The maximum number of processors that the workflow can use at once.

:func:`.mem`
^^^^^^^^^^^^

The maximum memory (GB) the the workflow can use at once.

Data
----

:func:`.sample`
^^^^^^^^^^^^^^^

The `sample <https://www.virtool.ca/docs/manual/guide/samples>`_ associated with the workflow run.

Returns a :class:`.Sample` object that can be used to access sample data. For analysis workflows, this will be the
sample being analyzed.

.. code-block:: python

    @step
    async def align(sample: Sample):
        # The library type of the sample: normal, srna, or amplicon.
        library_type: str = sample.library_type

        # Whether the sample Illumina dataset is paired or not.
        paired: bool = sample.paired



.. autoclass:: `virtool_workflow.data_model.samples.Sample`
    :members:

Analysis
--------

:func:`.analysis`
^^^^^^^^^^^^^^^^^

The analysis associated with the running workflow.

This fixture will be assigned if the workflow is responsible for populating a new analysis.


Non-Sample Data
---------------

Fixtures provide access to Virtool's non-sample data.

Non-sample data includes references and indexes, profile hidden Markov models (HMMs), and subtractions.

:func:`.hmms`
^^^^^^^^^^^^^

Provides all HMM annotations and the `profiles.hmm` file. Returns an :class:`.HMMs` object.

:func:`.indexes`
^^^^^^^^^^^^^^^^

The Virtool `reference indexes <https://www.virtool.ca/docs/manual/guide/indexes>`_ available for the current workflow.

Returns a :class:`list` of :class:`.Index` objects.

:func:`.subtractions`
^^^^^^^^^^^^^^^^^^^^^

The Virtool `subtractions <https://www.virtool.ca/docs/manual/guide/subtraction>`_ that were selected by the Virtool
user when the analysis workflow was started.

Returns a :class:`.list` of :class:`.Subtraction` objects.

Writing Fixtures
================

Fixtures are created by decorating functions with :func:`.fixture`.

.. code-block:: python

    @fixture
    def package_name() -> str:
        return "virtool-workflow==0.5.2"

Fixtures Using Other Fixtures
-----------------------------

Fixtures may depend on other fixtures.

Here is an example of how two fixtures (`package_name` and `package_version`) can be composed:

.. code-block:: python

    @fixture
    def package_name() -> str:
        return "virtool-workflow==0.5.2"

    @fixture
    def package_version(package_name: str):
        return package_name.split("==")[1]

Data Sharing with Fixtures
--------------------------

Once instantiated, a fixture, will persist through a workflow's entire execution. This means that mutable objects,
such as dictionaries, can be used to pass information between the steps of a workflow.

.. code-block:: python

    from virtool_workflow import fixture, step

    @fixture
    def mutable_fixture():
        return dict()

    @step
    def step_1(mutable_fixture):
        mutable_fixture["intermediate value"] = "some workflow state"

    @step
    def step_2(mutable_fixture):
        print(mutable_fixture["intermediate value"]) # "some workflow state"
