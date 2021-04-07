#!/bin/bash

workflow run --jobs-api-url http://localhost:9950/api "$@" --is-analysis-workflow true integration_test_job
