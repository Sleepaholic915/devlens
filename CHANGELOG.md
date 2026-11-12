# Changelog

Notable changes to DevLens are tracked here. The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

_No unreleased changes recorded._

## [0.1.0] - 2026-11-12

### Added
- Initial typed `InvestigationReport` schema and OpenAI Structured Outputs prototype.
- Business-rule validation for observations and next steps.
- pytest coverage for report validation, repository tools, tool dispatch, and mocked agent orchestration (25 tests passing locally: validation (5), repository tools (8), tool dispatch (4), mocked agent loop (4), fixture reproduction (2), evaluation summary (2)).
- Read-only Python repository inspection tools: `search_code` and `read_file`.
- OpenAI function-calling tool schemas and allowlisted tool dispatcher.
- Bounded sequential investigation loop and structured report generation.
- Experimental CLI entrypoint (`run_investigation.py`) and an intentionally buggy Python API fixture.
- First successful live CLI smoke test: five model-requested code inspections and a structured diagnosis of the missing-user 500 response (2026-11-10).
- Living system design document and release-oriented documentation.
- Deterministic agent-loop tests using mocked OpenAI Responses API calls.
- Structured tool execution traces with success and error information.
- Tests for tool error recovery and maximum tool-call budgets.
- Three reproducible API failure fixtures covering missing-user
  handling, incorrect total calculation, and missing authorization.
- JSON-based evaluation dataset with expected root causes.
- Evaluation runner supporting full-suite and single-case execution.
- Structured JSON evaluation artifacts containing investigation
  reports and tool traces.
- Evaluation summary utility reporting completion, report validity,
  tool success, and average tool calls.
- Fixture reproduction and evaluation-summary tests.
- A recorded three-case evaluation run completed all cases with eight successful tool calls and valid structured reports (small sample; not a root-cause accuracy benchmark).

### Verified for release
- 25 automated tests passed in a newly created Python 3.11 virtual environment.
- Fresh-environment live CLI investigation completed with 5/5 successful tool calls and a structured diagnosis.
- GitHub repository hygiene and release-readiness checks passed.

### Known limitations
- Mock tests and operational evaluation metrics do not verify model-driven diagnosis quality or evidence attribution.
- Current evaluation covers only three simulated Python API cases; automated root-cause grading is not implemented.
- Repository access protections are intended for trusted local code, not a security sandbox.

