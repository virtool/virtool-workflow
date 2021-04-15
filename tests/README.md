# Virtool Workflow Tests

## Environment Setup

```shell script
pip install poetry
poetry install
```

## Run Unit Tests Only

### Via `pytest` and `pytest-docker`

```shell script
poetry run pytest --ignore=integration
```

### Via Docker Compose

```shell script
poetry run docker-compose up --exit-code-from=pytest
```


## Build Jobs-API Image 

The `virtool/jobs-api` image is required for the integration tests.

The image can be build from local files, or from a branch of the `virtool` git repository.

### Build Locally

```shell script
poetry run workflow-test build jobs-api --path /path/to/virtool
```

### Build From Remote

```shell script
poetry run workflow-test build jobs-api --remote https://github.com/virtool/virtool@{branch}
```

You can also build off of a fork of `virtool/virtool` by providing it's URL.


## Run Integration Tests

### Inside Docker Container

```shell script
poetry run workflow-test integration
```
### In Local Environment

```shell script
poetry run pytest integration
```


