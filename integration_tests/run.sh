#!/bin/bash

set -e

(cd indexes && workflow test --is-analysis-workflow true index_integration_test_job)
(cd analysis && workflow test --is-analysis-workflow true analysis_integration_test_job)
(cd samples && workflow test --is-analysis-workflow true sample_integration_test_job)
(cd subtractions && workflow test --is-analysis-workflow true subtractions_integration_test_job)
