#!/usr/bin/env sh
# Run pytest along with Mongo and other dependencies

docker pull mongo:4.4.1

ID=$(docker run -d --network=host mongo)

pytest . "$@"

docker stop "$ID"
docker rm "$ID"