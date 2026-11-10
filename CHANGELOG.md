# Changelog

Notable changes to DevLens are tracked here. The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Initial typed `InvestigationReport` schema and OpenAI Structured Outputs prototype.
- Business-rule validation for observations and next steps.
- pytest coverage for report validation, repository tools, and tool dispatch (17 tests passing locally).
- Read-only Python repository inspection tools: `search_code` and `read_file`.
- OpenAI function-calling tool schemas and allowlisted tool dispatcher.
- Bounded sequential investigation loop and structured report generation.
- Experimental CLI entrypoint (`run_investigation.py`) and an intentionally buggy Python API fixture.
- First successful live CLI smoke test: five model-requested code inspections and a structured diagnosis of the missing-user 500 response (2026-11-10).
- Living system design document and release-oriented documentation.

### In progress
- Automated end-to-end regression tests and repeatability checks for the CLI investigation flow.
- Integration tests for multi-step agent behavior and execution-budget boundaries.

### Planned for v0.1.0
- At least three reproducible API failure fixtures with documented expected behavior.
- Repeatable CLI demo, automated agent-loop tests, and remaining release acceptance checks.

### Known limitations
- Unit tests do not verify model-driven diagnosis quality or evidence attribution.
- Repository access protections are intended for trusted local code, not a security sandbox.

<!-- At release time, create a dated section such as:
## [0.1.0] - YYYY-MM-DD
Move completed Unreleased items into it and tag the commit v0.1.0.
-->
