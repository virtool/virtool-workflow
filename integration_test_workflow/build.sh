#!/bin/bash

temp=$(mktemp -d build-vt-jobs-ap1-XXX)
cwd=$(pwd)

dockerfile=$(realpath api-server-Dockerfile)

# Ensure temporary directory is removed and return to previous directory
cmd="cd $cwd && rm -rf $temp"
trap "$cmd" SIGINT
trap "$cmd" EXIT

cd $temp

# Clone virtool/virtool before building `virtool/jobs-api` docker container
git clone --single-branch --branch ${1:-release/5.0.0} ${2:-https://github.com/virtool/virtool.git} && \
cd virtool && \
docker build -t virtool/jobs-api -f $dockerfile .
