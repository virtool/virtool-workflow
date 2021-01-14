#!/usr/bin/env sh
# Run pytest along with Mongo and other dependencies

echo "Starting MongoDB"
ID=$(sudo docker run -d --network=host mongo:4.4.1)

echo "Starting Redis"
REDIS=$(sudo docker run -d --network=host redis:6.0.8)

echo "Running pytest"


tox -- --disable-pytest-warnings "$@"

echo "Stopping MongoDB"
(sudo docker stop "$ID")
(sudo docker rm "$ID")

echo "Stopping Redis"
(sudo docker stop "$REDIS")
(sudo docker rm "$REDIS")