# Virtool Integration Tests

## Prerequisites 

Before running the integration tests ensure the following are installed.

1. docker
2. docker-compose 
3. virtool_workflow (`workflow test` command)

## Adding a New Test Case

1. Create a directory for the test case
    ```shell script
    mkdir my_test_case && cd my_test_case
    ```
2. Create a `workflow.py` file with your test case
3. Create a `DOCKERFILE` based on `virtool/workflow` 
    - Feel free to copy one from an existing test
4. Add a line in [run.sh](./run.sh) invoking the `workflow test` command 

## Running the Tests

To run the tests simply invoke the `run.sh` script

## Docker Root Problems

Depending on your linux groups configuration, you may require `sudo` to run docker. You
can allow `docker` to be run without `sudo` by following this [tutorial](https://www.configserverfirewall.com/docker/run-docker-without-sudo/).

Alternatively you can execute `run.sh` as root, ensuring that `virtool_workflow` is installed globally.

```shell script
sudo -H pip install virtool-workflow
sudo ./run.sh
```

`sudo -H` ensures that the system's home directory is used instead of the users.

