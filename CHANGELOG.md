# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.
## [Unreleased]

## [0.6.0] - 2021-07-21
### Changed

- `virtool_workflow.fixtures` moved to `fixtures`
- Fixture functions are stored in a context variable
### Added

- `fixture_context`, a context manager which creates a new context for fixtures
- `config` fixture, a dictionary containing all of the command line option values
- Sphinx plugin `autofixture` to provide special rendering for fixture functions
### Removed

- 'config fixtures' removed in favor of single fixture `config`
- `FixtureGroup` removed in favor of `fixture_context`
- The abstract classes for data provider classes `Abstract*Provider`

## [0.5.1]

### Changed

- Switch back to Sphinx for documentation
- Rename `temp_path` to `work_path`
- Improve error handling and exception messages
    - `WorkflowFixtureNotAvailable` replaced by `FixtureNotFound` and `FixtureBindingError`
    - Proper use of exception chaining
- Implements `provider` abstract classes using the Virtool Jobs API 
- Removes code relating to MongoDB from `virtool_worlflow` 
- Improves configuration fixtures
- Moves most functionality from `virtool_workflow_runtime` to `virtool_workflow`
    - `virtool_workflow_runtime` now contains code relating to the standalone runner process for workflows.
- Switches to `poetry` for dependency and build management
- Re-implement read trimming + caching
- Support colored logging
- Move `virtool/workflow` Dockerfile to repository root
- Run integration tests
- Config fixtures are funtions instead of `ConfigFixture` instances
- CLI options such as `--dev-mode` are now flags instead of boolean options.

### Added

- Add `indexes` fixture and tests
- Add integration tests against Virtool's jobs API
- Add `provider` abstract classes
    - Avoid accessing the database directly
    - Simplify testing by allowing for alternate implementations
- Add `FixtureGroup`
- Add dataclasses for various domain objects
    - Jobs
    - Subtractions
    - Indexes
    - References
    - ...
- Github action for testing the docker build
- Github action for testing the PyPi package validity
- Github action for verifying this changelog
- Move `virtool/workflow` Dockerfile to repository root
- Github action to create github releases
- Github action to perform a a nightly build
- Github action to create a release branch
- Github action to run integration tests
- Github action to performa a nightly build
    - Releases `virtool/workflow:nightly` docker image
- `workflow test` subcommand
    - Runs a workflow in a test environment using docker-compose
- Github action to push changes from master branch to develop branch

