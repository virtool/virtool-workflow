#!/usr/bin/env sh
# Run pytest along with Mongo and other dependencies

[ "$1" != "--no_pull" ] && \
  docker pull mongo:4.4.1 && \
  docker pull redis:6.0.8

echo "Starting MongoDB"
ID=$(docker run -d --network=host mongo)

echo "Starting Redis"
REDIS=$(docker run -d --network=host redis)

echo "Running pytest"


[ "$1" == "--no_pull" ] && \
  pytest --disable-pytest-warnings "${@:3}" || \
  pytest --disable-pytest-warnings "$@"

echo "Stopping MongoDB"
(docker stop "$ID")
(docker rm "$ID")

echo "Stopping Redis"
(docker stop "$REDIS")
(docker rm "$REDIS")