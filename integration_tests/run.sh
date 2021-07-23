#!/bin/bash

set -e

(cd .. && docker build -t virtool/workflow .)
(cd indexes && workflow test --is-analysis-workflow)
(cd analysis && workflow test --is-analysis-workflow)
(cd samples && workflow test --is-analysis-workflow)
(cd subtractions && workflow test --is-analysis-workflow)
