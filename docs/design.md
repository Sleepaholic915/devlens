# DevLens — System Design

**Document status:** Active / living design  
**Project phase:** Pre-MVP  
**Next target release:** `v0.1.0`  
**Last revised:** 2026-11-12

This document describes the architecture, design rationale, interfaces, safety constraints, and planned evolution of DevLens. It is organized by **capability and release**, not by study day. Statements are labeled **Implemented**, **In progress**, or **Planned** where appropriate.

## 1. Problem and goals

Backend API failures often surface as opaque HTTP errors. Developers need to connect symptoms to source code and logs while avoiding premature conclusions.

DevLens aims to:

1. Accept an API failure description (endpoint, expected/actual status, response, optional logs).
2. Inspect a developer-selected Python repository through restricted read-only tools.
3. Produce a typed investigation report with observations, hypotheses, and next steps.
4. Make diagnostic claims traceable to available evidence as the evidence model evolves.
5. Remain testable, bounded, and understandable without heavyweight infrastructure.

### Non-goals for v0.1.0

- Automatically changing source code or production infrastructure
- Arbitrary command or shell execution
- Guaranteed root-cause determination
- General-purpose codebase Q&A or semantic vector search
- Web UI, database, distributed services, or multi-agent coordination

## 2. Architecture

**Style:** Python modular monolith. A single application contains separate modules for schema, validation, repository tools, model interaction, and orchestration.

```text
User / CLI
   |
   v
Failure input -> Agent harness <-> OpenAI Responses API
                    |
                    v
             Tool dispatcher
                    |
             +------+------+
             |             |
         search_code     read_file
             |             |
             +------v------+
              Local Python repo
                    |
                    v
          InvestigationReport (Pydantic)
                    |
                    v
             Business validator
                    |
                    v
               CLI output
```

**Current state:** Structured reports, business validation, repository tools, and tool dispatch are implemented and unit tested. The CLI and agent loop have completed live investigations on three simulated API failures; mocked agent-loop tests pass, and a three-case evaluation runner is implemented. Repeated real-model regression checks remain pending.

### Module responsibilities

| Module | Responsibility | Status |
| --- | --- | --- |
| `devlens/models.py` | Typed investigation report | Implemented |
| `devlens/validation.py` | Business-rule validation | Implemented |
| `devlens/tools.py` | Repository-scoped source inspection | Implemented; unit tested |
| `devlens/agent.py` | Tool definitions, allowlisted dispatcher, bounded agent loop, final report parsing | Implemented; mocked agent-loop tests passed; live CLI exercised |
| `run_investigation.py` | CLI input, investigation execution, report display | Implemented; live CLI exercised |
| `tests/` | Validation, repository tools, dispatcher, mocked agent-loop, and fixture/evaluation tests | 25 tests passing in the reported full pytest suite |
| `evals/cases.json` | Evaluation cases and expected root causes | Implemented |
| `evals/run_evals.py` | Run cases and persist JSON investigation artifacts | Implemented; live run completed |
| `evals/summarize.py` | Aggregate operational evaluation metrics | Implemented; summary executed |

## 3. Data contract

**Implemented** report schema:

```python
from pydantic import BaseModel

class InvestigationReport(BaseModel):
    observations: list[str]
    hypotheses: list[str]
    next_steps: list[str]
```

- **Observations:** facts supported by provided inputs or inspected evidence.
- **Hypotheses:** plausible but unconfirmed explanations; an empty list is valid.
- **Next steps:** concrete ways to investigate or verify.

**Implemented** business checks require at least one observation and one next step. The schema itself does not establish factual correctness.

**Planned:** structured evidence references such as `{file, line_start, line_end, excerpt}` and stronger attribution requirements for observations.

## 4. Repository inspection tools

**Status:** Implemented and unit tested; exercised by multiple live CLI investigations.

### Implemented interfaces

- `search_code(query: str) -> list[dict]`: literal case-insensitive substring matches in Python source files, including repository-relative path, line number, and excerpt.
- `read_file(relative_path: str, start_line: int, end_line: int) -> dict`: bounded line-numbered excerpt from a Python file.

### Safety and resource controls

- Scope access to a caller-selected repository root.
- Reject absolute paths and traversal outside the root.
- Restrict to Python source files for the initial MVP.
- Skip generated/vendor/virtual-environment directories.
- Limit file size, search hits, line ranges, and returned content.
- Expose no shell execution or write tools to the model.

**Known limitation:** Resolving paths before opening them is not a complete defense against symlink races or concurrently modified untrusted repositories. MVP use is restricted to trusted local repositories; stronger isolation is future work.

### Design choice: standard library vs ripgrep

Start with `pathlib` and standard-library file scanning for low setup cost and easy tests. Reconsider `ripgrep` when repository size or search latency justifies an external dependency.

## 5. Agent orchestration

**Status:** Implemented as a prototype; live CLI investigations and deterministic mocked agent-loop tests have succeeded.

The model proposes a function call; the application dispatches allowlisted tool names and arguments to `CodeTools`, serializes the result, and returns it to the model. The model does not directly execute local Python functions or shell commands.

### Implemented investigation flow

1. The CLI passes the failure description and selected repository root to `investigate()`.
2. `responses.create()` provides strict definitions for `search_code` and `read_file`.
3. The harness extracts `function_call` items from `response.output` **before inspecting the `calls` variable**.
4. `execute_tool()` runs the allowed Python tool and serializes a success or error result.
5. The harness appends a `function_call_output` item with the matching `call_id` and continues the conversation.
6. The loop stops when the model stops requesting tools or the configured tool-call budget is exhausted.
7. A separate `responses.parse()` call produces an `InvestigationReport`, which is checked by `validate_report()`.

The default budget is eight tool calls, and `parallel_tool_calls=False` requests sequential tool use. The application also checks for unexpectedly multiple calls. These are controls for a prototype, not a complete model-request, time, or token budget.

### Mock Responses API testing

**Implemented and passing (as reported after fixing the variable-order bug).** `tests/test_agent.py` uses `unittest.mock.Mock` and simulated response objects to exercise the orchestration code without calling the real API. Mocking makes the sequence of tool requests deterministic and avoids API costs. The new scenarios cover:

- Tool execution, conversation continuation, and a typed final report.
- Tool-error recovery across two model responses.
- Enforcement of `max_tool_calls`.
- Rejection of a nonpositive tool-call budget.

After correcting the order of `calls` extraction and validation, the user confirmed that all 21 then-existing tests passed. Mock tests verify orchestration behavior; they do not establish the accuracy of model diagnoses.

### Tool error recovery

**Implemented at the dispatcher boundary; mocked multi-turn recovery tested.** `execute_tool()` returns structured JSON for success (`ok: true`, `result`) or failure (`ok: false`, `error`). A tool error is returned to the model as a normal tool result so the model can attempt a corrected call. In the first live demo, the model requested a 100-line read (above the 80-line limit) and later requested a 30-line read. Subsequent live CLI traces confirmed `[ERROR]` on oversized reads followed by successful corrected reads.

### Structured tool trace and observability

**Implemented and exercised in live CLI runs.** The trace is intended to store each tool name, JSON arguments, `ok` status, optional result, and optional error. The CLI can display `[OK]` or `[ERROR]` and an error reason, making tool execution easier to debug. This is an in-memory diagnostic trace, not persistent logging, and it does not by itself verify evidence quality.

### Harness controls and remaining gaps

**Implemented:** explicit tool allowlist; strict tool argument schemas; Python-side path and read limits; bounded tool-call count; tool-error serialization; completed-response checks; final Pydantic parsing and business validation; in-memory tool trace.

**Pending:** repeated live-model end-to-end regression checks; total model-request, token, and wall-clock budgets; comprehensive API error handling and recovery; independently verified evidence attribution.

**Known edge case to test:** response continuation and tool-call bookkeeping at the budget boundary, especially if the model requests further tools. The tool-call count alone does not cap total model usage.

### Separation of reliability concerns

1. **Exception handling:** network, API, parsing, and tool-execution failures.
2. **Response validation:** schema and business constraints.
3. **Evidence verification:** whether observations are supported by actual source material.
4. **Evaluation:** effectiveness and correctness across a suite of known failures.

These checks are complementary, not interchangeable.

## 6. Technology decisions

| Decision | Rationale | Revisit when |
| --- | --- | --- |
| Python | Fast iteration, strong AI ecosystem, readable tooling | Requirements demand another runtime |
| OpenAI SDK directly | Learn tool-calling protocol and keep abstraction small | Workflow complexity warrants orchestration framework |
| Pydantic | Typed boundary between model output and application logic | Contract needs substantial redesign |
| pytest | Fast deterministic unit tests and fixtures | Additional integration/evaluation infrastructure needed |
| Modular monolith | Clear boundaries without deployment overhead | Independent scaling or team ownership emerges |
| No database for MVP | No persistent multi-user history required yet | Durable traces and querying become requirements |
| CLI before API/UI | Fastest route to end-to-end evidence-backed demo | CLI workflow is stable |

## 7. Testing and release acceptance

### Current automated tests

**Latest reported full pytest run: 25 passed in 0.64s (25 collected)**. The suite includes unit tests, mocked agent-loop tests, fixture reproduction tests, and evaluation-summary tests.

- **5 validation tests:** valid reports, empty hypotheses, required observations/next steps.
- **8 repository tool tests:** search, case-insensitivity, bounded reads, path restrictions, file types, result limit.
- **4 dispatcher tests:** successful search, unknown tool rejection, invalid JSON, and path escape rejection.
- **4 mocked agent-loop tests:** tool execution/continuation, error recovery, tool budget, and invalid budget.
- **2 fixture reproduction tests:** incorrect total and missing authorization.
- **2 evaluation-summary tests:** metric calculations and empty evaluation results.

These deterministic tests do not measure LLM diagnosis accuracy. Separate live CLI investigations and a three-case evaluation run exercised the investigation pipeline.

### Initial live CLI verification (2026-11-10)

A manual run investigated `GET /api/users/999` (expected 404, observed 500) against `examples/buggy_api`.

- The agent made **five tool requests** in order: `search_code("/api/users")`, `search_code("users")`, `read_file("app.py", 1, 100)`, `read_file("app.py", 1, 30)`, and `search_code("404")`.
- The final report correctly identified the unchecked `USERS.get(user_id)` lookup and the broad exception handler that converts errors into a 500-style response.
- The report explicitly acknowledged that the example repository does not show HTTP route wiring, so it did not claim to have verified the actual route.
- The first `read_file` request exceeded the configured 80-line limit; the subsequent 30-line request illustrates recovery from a likely tool validation error. The CLI trace did not print tool outputs, so the precise result of each request was not independently inspected.
- This is **one manual smoke test**, not a reproducible evaluation suite or proof of consistent diagnosis quality.

### Evaluation framework

DevLens includes a small evaluation dataset consisting of three
reproducible API failure scenarios:

1. Missing user handling: an unknown user ID produces a 500 instead
   of the expected 404.
2. Incorrect total calculation: a fractional discount is incorrectly
   subtracted as a fixed amount.
3. Missing authorization: an order is returned without checking
   resource ownership.

Each evaluation case defines a failure description and expected
root cause. Ground-truth information is stored separately from the
failure description passed to the agent.

The evaluation runner executes each investigation and records:
- Investigation status
- Structured investigation report
- Tool execution trace
- Number of tool calls

The summary utility calculates:
- Completion rate
- Report validity rate
- Tool success rate
- Average tool calls per case

These metrics measure execution reliability and output validity.
Root-cause correctness is currently assessed through manual review
rather than automated grading.

Current limitations:
- Only three small, simulated Python API scenarios are evaluated.
- Results from one evaluation run do not establish statistical reliability.
- The fixtures do not exercise a deployed HTTP service.
- Automated root-cause scoring is not yet implemented.

### Recorded evaluation baseline

A saved run (`20261111T150652Z`) recorded 3/3 completed investigations, 8/8 successful tool calls, and 3/3 valid reports (2.67 calls/case). These are **operational metrics**, not automated root-cause accuracy. The saved trace still contained answer-revealing fixture docstrings; the baseline must be rerun after final fixture cleanup for a cleaner assessment.

### Final release verification (2026-11-12)

A clean Python 3.11 virtual environment installed declared dependencies and passed all 25 tests. A fresh live investigation of the missing-user fixture completed with five successful tool calls, zero tool errors, and a structured report that identified the missing-user lookup and broad exception handler while explicitly noting unverified HTTP route wiring. Repository readiness checks passed. These checks establish MVP operability, not generalized diagnostic accuracy.

### v0.1.0 acceptance criteria

- [x] A documented CLI command accepts a failure case and repository path (manually exercised).
- [x] Agent can request `search_code` and `read_file` and complete a multi-step investigation (manual smoke test).
- [x] Tool execution has repository-scoped checks and a tool-call budget (unit-tested components; not a hardened sandbox).
- [x] A live investigation produced an `InvestigationReport` and passed business checks.
- [x] At least three reproducible bug fixtures are documented and exercised (simulated handlers).
- [x] Full pytest suite passes: 25/25 tests in a newly created `.venv-release` environment.
- [x] Fresh-environment live CLI smoke test: five successful tool calls and a structured report for the missing-user scenario.
- [x] GitHub repository hygiene and release-readiness checks passed.
- [x] README commands, dependency setup, and fresh-environment reproducibility reviewed.
- [ ] Tag `v0.1.0` only after all release criteria are satisfied.

## 8. Release roadmap

| Version | Theme | Exit condition |
| --- | --- | --- |
| `v0.1.0` | Functional MVP | End-to-end CLI agent + tools + tests + demo fixtures |
| `v0.2.0` | Evidence and reliability | Evidence attribution, stronger guardrails, expanded/repeated evaluation |
| `v0.3.0` | API and persistence | HTTP interface and stored investigations, if needed |
| `v1.0.0` | Stable release | Documented, tested, reproducible, stable core contract |
| `v1.0.1+` | Maintenance | Bug fixes and security patches |
| `v1.1.0+` | Extensions | Backward-compatible features |

Roadmap versions are targets, not commitments. Release scope can change based on evaluation and actual needs.

## 9. Open design questions

- What is the minimal evidence-reference schema for verified observations?
- How should the harness respond to insufficient evidence: report uncertainty, retry, or ask for logs?
- How should the agent handle continuation and tool-call budgets at edge cases, including interrupted or incomplete tool exchanges?
- What iteration/token budgets produce useful results at acceptable cost?
- How should tests measure diagnosis quality versus mere schema compliance?
- When do repository scale and performance justify ripgrep or indexing?

## 10. Documentation and change policy

- Update this document when architecture, tool contracts, safety rules, or release scope changes.
- Update README when user-visible functionality, setup, or usage changes.
- Record notable changes under `CHANGELOG.md` **Unreleased**; move them under a version heading when a release is tagged.
- Prefer feature-oriented commits (`feat`, `fix`, `test`, `docs`, `refactor`, `chore`) and meaningful pull requests or commit messages.
- Never mark planned work as implemented solely because code has been drafted.



