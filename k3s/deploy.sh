#!/bin/bash
# Deploy The Virtool Server And Jobs API in Kubernetes.

# Redis
kubectl apply -f ./redis/deployment.yml
kubectl apply -f ./redis/service.yml

# Postgres
kubectl apply -f ./postgres/config.yml
kubectl apply -f ./postgres/volume.yml
kubectl apply -f ./postgres/deployment.yml
kubectl apply -f ./postgres/service.yml

# Mongo
kubectl apply -f ./mongo/volume.yml
kubectl apply -f ./mongo/deployment.yml
kubectl apply -f ./mongo/service.yml

# Jobs API
kubectl apply -f ./jobsAPI/deployment.yml
kubectl apply -f ./jobsAPI/service.yml

# Virtool Server
kubectl apply -f ./server/deployment.yml
kubectl apply -f ./server/service.yml