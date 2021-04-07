#!/bin/bash

set -e

format='\e[1;34m%-6s\e[m'

_print_one_line(){
    printf $format "$1"
    echo -e "\n"
}

_print() {
    echo -e "\n"
    _print_one_line "$1"
}


_help() {
    echo "Build the docker images for the 'virtool_workflow' integration tests."
    echo
    echo "Syntax: ./build.sh [--virtool-repo|--virtool-workflow-repo]"
    echo "Options:"
    echo "--virtool-repo             The URL of the virtool github repo (to use your fork)."
    echo "--virtool-branch           The name of the branch to pull from the virtool repo." 
    echo "--virtool-workflow-repo    The URL of the virtool-workflow github repo (to use your fork)."
    echo
}


# Parse options
while [[ $# -gt 0 ]] 
do
    key="$1"
    case $key in
        --virtool-workflow-repo)
            VIRTOOL_WORKFLOW_REPO="$2"
            shift
            shift 
        ;;
        --virtool-repo)
            VIRTOOL_REPO="$2"
            shift
            shift 
        ;;
        --virtool-branch)
            VIRTOOL_BRANCH="$2"
            shift 
            shift
        ;;
        --help)
            _help
            exit
        ;;
        
    esac
done

virtool_workflow_repo=${VIRTOOL_WORKFLOW_REPO:-"https://github.com/virtool/virtool-workflow"}
virtool_repo=${VIRTOOL_REPO:-"https://github.com/virtool/virtool"}
virtool_branch=${VIRTOOL_BRANCH:-"release/5.0.0"}

cwd=$(pwd)

dockerfile=$(realpath api-server-Dockerfile)
test_dockerfile=$(realpath workflow/Dockerfile)
workflow_latest_dockerfile=$(realpath latest-workflow-Dockerfile)

_print "Building 'virtool/workflow' image with the latest version of 'virtool_workflow'..."
docker build -t virtool/workflow -f $workflow_latest_dockerfile --build-arg "VIRTOOL_WORKFLOW_REPO=$virtool_workflow_repo" .

_print "Building 'virtool/integration_test_workflow'..."
docker build -t virtool/integration_test_workflow -f $test_dockerfile workflow

temp=$(mktemp -d build-vt-jobs-ap1-XXX)
_print_one_line "Created temporary directory... $temp"

# Ensure temporary directory is removed and return to previous directory
cmd="cd $cwd && rm -rf $temp"
trap "$cmd" SIGINT
trap "$cmd" EXIT


cd $temp

_print "Building 'virtool/job-api' with the latest changes..."
git clone --single-branch --branch $virtool_branch $virtool_repo && \
cd virtool && \

docker build -t virtool/jobs-api -f $dockerfile .

_print DONE
