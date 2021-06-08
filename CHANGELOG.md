# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [Unreleased]

### Changed

- Switch back to Sphinx for documentation
- Add `indexes` fixture and tests
- Rename `temp_path` to `work_path`
- Add `provider` abstract classes
    - Avoid accessing the database directly
    - Simplify testing by allowing for alternate implementations
- Improve error handling and exception messages
    - `WorkflowFixtureNotAvailable` replaced by `FixtureNotFound` and `FixtureBindingError`
    - Proper use of exception chaining
- Introduce `FixtureGroup`
- Add dataclasses for various domain objects
    - Jobs
    - Subtractions
    - Indexes
    - References
    - ...
- Implements `provider` abstract classes using the Virtool Jobs API 
- Removes code relating to MongoDB from `virtool_worlflow` 
- Improves configuration fixtures
- Moves most functionality from `virtool_workflow_runtime` to `virtool_workflow`
    - `virtool_workflow_runtime` now contains code relating to the standalone runner process for workflows.
- Switches to `poetry` for dependency and build management
- Re-implement read trimming + caching
- Support colored logging
- Add integration tests against Virtool's jobs API
- Move `virtool/workflow` Dockerfile to repository root

### Added

- Github action for testing the docker build
- Github action for testing the PyPi package validity
- Github action for verifying this changelog
- Move `virtool/workflow` Dockerfile to repository root
- Github action to create github releases
- Github action to create a release branch
- Github action to run integration tests
- Github action to performa a nightly build
    - Releases `virtool/workflow:nightly` docker image

