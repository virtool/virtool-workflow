# Virtool Integration Tests

## Setting Up a Test Case

1. Create a directory for the test case
    ```shell script
    mkdir my_test_case && cd my_test_case
    ```
2. Create a `.env` file as follows:
    ```env
    COMPOSE_FILE="../docker-compose.api.yml:../docker-compose.workflow.yml"
    VT_BUILD_CONTEXT=https://github.com/<username>/virtool.git#<branch>
    VT_DOCKERFILE_PATH=docker/jobs-api/Dockerfile
    VT_JOB_ID=<job-id>
    WORKFLOW_NAME=<workflow-name>
    WORKFLOW_DIR=<test-case-directory-name>
    ```
    * `COMPOSE_FILE` specifies the docker-compose file(s) to be used when running `docker-compose up`
    * `VT_BUILD_CONTEXT` is the repository or directory containing the desired version of the `virtool` source.
    * `VT_JOB_ID` is the ID of the virtool job which will be executed in this test.
    * `WORKFLOW_NAME` the name of the workflow for this test.
    * `WORKFLOW_DIR` the name of the test case directory created in step 1.

The `VT_BUILD_CONTEXT` can also be a path (`VT_BUILD_CONTEXT=/path/to/virtool`).

### Adding Arguments to the `workflow run` Command

any additional arguments to the `workflow run` command you can be included in the value of the
`VT_ADD_ARGS` environment variable. 

```env
VT_ADD_ARGS="--dev-mode true --data-path /data/path"
```

You can also add arguments only for a specific `docker-compose up` run as follows:

```env
VT_ADD_ARGS="--dev-mode true --data-path /data/path" docker-compose up --exit-code-from workflow
```

## Running the Tests

To run any of the integration test cases simply `cd` into the appropriate directory and run `docker-compose up`.

For example to run the integration test for the `samples` fixture:

```shell script
cd integration_tests/samples
docker-compose up --exit-code-from workflow
```
