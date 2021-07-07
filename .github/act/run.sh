#!/bin/bash
# Run `act` to test github actions

# Test that `poetry publish` dry run succeeds
act -s PYPI_USERNAME="invalid" -s PYPI_TOKEN="invalid" -j pypi-check

act -j pypi-publish