#!/bin/sh

temp=$(mktemp -d build-vt-jobs-ap1-XXX)

cwd=$(pwd)
dockerfile=$(realpath api-server-Dockerfile)

cd $temp
# Clone virtool/virtool before building `virtool/jobs-api` docker container
git clone --single-branch --branch release/5.0.0 https://github.com/virtool/virtool.git
cd virtool

docker build -t virtool/jobs-api -f $dockerfile .

cd $cwd
rm -rf $tmp_dir
