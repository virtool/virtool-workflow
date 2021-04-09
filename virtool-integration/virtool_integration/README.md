# Virtool Workflow Integration Tests

## Installation

The `virtool_integration` package can be installed by;

```shell script
pip install .
```

Or to run in a poetry virtual environment;

```
poetry install
```

## Building the Docker Images

The `workflow-test` script is included in the pip/poetry install. This utility is used to build the required images
with the latest version of the code. 

```shell script
workflow-test build all --help
```

```text
    Usage: workflow-test build all [OPTIONS]

      Build all of the required images.

    Options:
      --virtool-workflow-remote TEXT  The virtool-workflow git repository to pull
                                      from.

      --virtool-workflow-path PATH    The path to a local clone of the virtool-
                                      workflow git repository.

      --virtool-path TEXT             The path to a local clone of the virtool git
                                      repository.

      --virtool-remote TEXT           The virtool git repository to pull from.
      --help                          Show this message and exit.
```


You can also build individual images using the subcommands of `workflow-test build`.

```shell script
workflow-test build --help
```

```text
    Usage: workflow-test build [OPTIONS] COMMAND [ARGS]...

      Build the required docker images with the latest version of the code.

    Options:
      --help  Show this message and exit.

    Commands:
      all          Build all of the required images.
      integration  Build the `virtool/integration_test_workflow` image.
      jobs-api     Build the `virtool/jobs-api` image.
      workflow     Build the `virtool/workflow` image.
```

Each subcommand accepts either a `--path` or `--remote` option indictating which version 
of the code should be used.

For example, to build the `virtool/workflow` image based on the master branch of the `virtool/virtool_workflow` repository;


```shell script
workflow-test build workflow --remote https://github.com/virtool/virtool-workflow@master
```


## Running the Tests

Once the docker images have been build using the desired version of the source code, you can start the test environment using;

```shell script
workflow-test up
```

This simply runs a `docker-compose up` command with some options preset.
