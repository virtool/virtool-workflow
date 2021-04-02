#!/bin/bash

indent() { sed 's/^/  /'; }

printf '\e[1;34m%-6s\e[m' $'Running build script...\n'
./build.sh | indent
printf '\e[1;34m%-6s\e[m' $'Starting docker-compose...\n'
docker-compose up --exit-code-from=integration_test_workflow | indent
