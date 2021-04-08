#!/bin/bash

format='\e[1;34m%-6s\e[m'

_print() {
    echo -e "\n"
    printf $format "$1"
    echo -e "\n"
}

_print 'Running build script...'
./build.sh "$@" && \
_print 'Starting docker-compose...' && \
docker-compose up --exit-code-from=integration_test_workflow
_print "DONE"
