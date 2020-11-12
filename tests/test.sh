#!/usr/bin/env sh
# Run pytest along with Mongo and other dependencies

if [ "$1" != "--no-pull" ]
then
  sudo docker pull mongo:4.4.1 && docker pull redis:6.0.8
fi

echo "Starting MongoDB"
ID=$(sudo docker run -d --network=host mongo)

echo "Starting Redis"
REDIS=$(sudo docker run -d --network=host redis)

echo "Running pytest"


if [ "$1" = "--no-pull" ]
then
  tox -- --disable-pytest-warnings "${@:3}"
else
  tox -- --disable-pytest-warnings "$@"
fi

echo "Stopping MongoDB"
(sudo docker stop "$ID")
(sudo docker rm "$ID")

echo "Stopping Redis"
(sudo docker stop "$REDIS")
(sudo docker rm "$REDIS")