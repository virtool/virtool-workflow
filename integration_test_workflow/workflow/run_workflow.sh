#!/bin/bash

workflow run --jobs-api-url http://localhost:9990/api "$@" --is-analysis-workflow true integration_test_job
