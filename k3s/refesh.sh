#!/bin/bash

# Reload a deployment (so that new docker container will be used)

kubectl scale "deployments/$1" --replicas=0
kubectl scale "deployments/$1" --replicas=1
