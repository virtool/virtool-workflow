#!/usr/bin/env sh
# Run pytest along with Mongo and other dependencies

if [ "$1" != "--no-pull" ]
then
  docker pull mongo:4.4.1 && docker pull redis:6.0.8
fi

echo "Starting MongoDB"
ID=$(docker run -d --network=host mongo)

echo "Starting Redis"
REDIS=$(docker run -d --network=host redis)

echo "Running pytest"


if [ "$1" = "--no-pull" ]
then
  pytest --disable-pytest-warnings "${@:3}"
else
  pytest --disable-pytest-warnings "$@"
fi

echo "Stopping MongoDB"
(docker stop "$ID")
(docker rm "$ID")

echo "Stopping Redis"
(docker stop "$REDIS")
(docker rm "$REDIS")