# Virtool Integration Tests

These integration tests are to ensure that the utilities in `virtool_workflow` function correctly
with the *Virtool Jobs API*.

## Setting Jobs API Version

The version of the jobs API code which is used can be changed by editing the `.env` file.

```env
VT_BUILD_CONTEXT=https://github.com/<username>/virtool.git#<branch>
VT_DOCKERFILE_PATH=docker/jobs-api/Dockerfile
```

The `VT_BUILD_CONTEXT` variable is a URL specifying which github repository to build from.
A local clone of the virtool repository can be used instead by setting `VT_BUILD_CONTEXT=/path/to/virtool`.

## Running the Tests

To run any of the integration test cases simply `cd` into the appropriate directory and run `docker-compose up`.

For example to run the integration test for the `samples` fixture:

```shell script
cd integration_tests/samples
docker-compose up 
```

