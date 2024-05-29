Contributing
************

`Poetry <https://python-poetry.org>`_ is used to manage the dependencies and virtual
environment.

Install Dependencies
====================

1. `Install Poetry <https://python-poetry.org/docs/#installation>`_

2. Install dependencies

    .. code-block:: shell

        poetry install

Run Commands In The Virtual Environment
=======================================

.. code-block:: shell

    poetry run <command>


Testing
=======

.. code-block:: shell

    # Start the test environment.
    docker compose up -d

    # Run tests in a container with access to Redis and the required tools in PATH.
    docker exec test poetry run pytest

Documentation
=============

Build
-----

Live Preview
------------

.. code-block:: shell

    poetry run sphinx-autobuild docs docs/_build virtool-workflow
