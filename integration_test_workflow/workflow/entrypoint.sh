#!/bin/sh
# Entrypoint script for the integration test workflow.

workflow run "$@" integration_test_job
