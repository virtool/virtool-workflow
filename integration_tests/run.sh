#!/bin/bash

set -e

(cd indexes && workflow test --is-analysis-workflow index_integration_test_job)
(cd analysis && workflow test --is-analysis-workflow analysis_integration_test_job)
(cd samples && workflow test --is-analysis-workflow sample_integration_test_job)
(cd subtractions && workflow test --is-analysis-workflow subtractions_integration_test_job)
