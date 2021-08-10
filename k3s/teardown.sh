#!/bin/sh
# Completely tear down the k3s deployment

for f in $(find . -type f -name *.yml);
do 
    kubectl delete -f "$f"
done

