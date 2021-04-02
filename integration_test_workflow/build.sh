#!/bin/bash

temp=$(mktemp -d build-vt-jobs-ap1-XXX)
cwd=$(pwd)

dockerfile=$(realpath api-server-Dockerfile)
test_dockerfile=$(realpath workflow/Dockerfile)
workflow_latest_dockerfile=$(realpath latest-workflow-Dockerfile)

# Build `virtool/workflow` with the latest changes
docker build -t virtool/workflow -f $workflow_latest_dockerfile .


# Build integration test workflow container
docker build -t virtool/integration_test_workflow -f $test_dockerfile workflow

# Ensure temporary directory is removed and return to previous directory
cmd="cd $cwd && rm -rf $temp"
trap "$cmd" SIGINT
trap "$cmd" EXIT


cd $temp

# Clone virtool/virtool before building `virtool/jobs-api` docker container
git clone --single-branch --branch ${1:-release/5.0.0} ${2:-https://github.com/virtool/virtool.git} && \
cd virtool && \

docker build -t virtool/jobs-api -f $dockerfile .
