#!/bin/sh
# Completely tear down the k3s deployment

kubectl delete deployments --all
kubectl delete services --all
kubectl delete pvc --all