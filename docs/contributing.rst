Contributing
************

`Poetry <https://python-poetry.org>`_ is used to manage the dependencies and virtual environment.

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

    cd tests
    docker-compose up --build --exit-code-from pytest

Documentation
=============

Use the `Sphinx docstring format <https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html>`_.

Build
-----

.. code-block:: shell

    (cd docs && ./build-docs.sh)


Live Preview
------------

.. code-block:: shell

    pip install sphinx-autobuild
    sphinx-autobuild sphinx sphinx/_docs/html
