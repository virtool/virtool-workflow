#!/bin/bash

workflow run --jobs-api-url http://localhost:9950 --is-analysis-workflow true integration_test_workflow
