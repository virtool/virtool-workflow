#!/bin/bash
# Deploy The Virtool Server And Jobs API in Kubernetes.


declare -a manifests=(
    "./redis/deployment.yml"
    "./redis/service.yml"
    "./mongo/volume.yml"
    "./mongo/deployment.yml"
    "./mongo/service.yml"
    "./postgres/volume.yml"
    "./postgres/config.yml"
    "./postgres/deployment.yml"
    "./postgres/service.yml"
    "./server/volume.yml"
    "./server/deployment.yml"
    "./server/service.yml"
    "./jobsAPI/deployment.yml"
    "./jobsAPI/service.yml"
    "./create_sample/deployment.yml"
)


for manifest in ${manifests[@]};
do 
    kubectl apply -f $manifest
done

function get_port {
    kubectl get services | 
        grep -E $1 | 
        tr -s ' ' | 
        cut -d' ' -f5 | 
        cut -d':' -f2 | 
        cut -d'/' -f1
}

echo "Virtool Server: http://localhost:$(get_port server)"
echo "Jobs API: http://localhost:$(get_port job)/api"

