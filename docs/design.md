# DevLens — System Design

**Document status:** Active / living design  
**Project phase:** Pre-MVP  
**Next target release:** `v0.1.0`  
**Last revised:** 2026-11-06

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

**Current state:** Structured report generation and business validation are implemented. Repository tools are in progress; the harness and end-to-end CLI are planned.

### Module responsibilities

| Module | Responsibility | Status |
| --- | --- | --- |
| `devlens/models.py` | Typed investigation report | Implemented |
| `devlens/validation.py` | Business-rule validation | Implemented |
| `devlens/tools.py` | Repository-scoped source inspection | In progress |
| Agent harness / dispatcher | Bound model-requested tools and feed results back | Planned |
| CLI entrypoint | Input, execution, and report display | Planned |
| `tests/` | Deterministic validation and tool tests | Implemented / expanding |

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

**Status:** In progress; integration and tests must be verified before marking complete.

### Intended interfaces

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

**Status:** Planned for `v0.1.0`.

The model proposes a function call; the application validates its name and arguments, executes an allowlisted tool, and returns the result to the model. The model must not receive arbitrary filesystem or process execution privileges.

### Required harness controls

- Explicit tool allowlist and argument validation
- Maximum iterations / tool calls
- Bounded tool output and timeouts where practical
- Clear handling of API failures, tool errors, and incomplete responses
- Final Pydantic parsing and business validation
- Investigation trace useful for debugging and evaluation

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

- Valid structured report passes business validation.
- Empty hypotheses are allowed.
- Empty observations or next steps are rejected.

### v0.1.0 acceptance criteria

- [ ] A documented CLI command accepts a failure case and repository path.
- [ ] Agent can request and receive `search_code` and `read_file` results.
- [ ] Tool execution is bounded and repository-scoped.
- [ ] Final report conforms to `InvestigationReport` and passes business checks.
- [ ] At least three reproducible bug fixtures are documented and exercised.
- [ ] Tests pass in a fresh virtual environment.
- [ ] README accurately reflects working features; demo can be reproduced.
- [ ] Release tagged `v0.1.0` only after criteria are satisfied.

## 8. Release roadmap

| Version | Theme | Exit condition |
| --- | --- | --- |
| `v0.1.0` | Functional MVP | End-to-end CLI agent + tools + tests + demo fixtures |
| `v0.2.0` | Evidence and reliability | Evidence attribution, stronger guardrails, evaluation baseline |
| `v0.3.0` | API and persistence | HTTP interface and stored investigations, if needed |
| `v1.0.0` | Stable release | Documented, tested, reproducible, stable core contract |
| `v1.0.1+` | Maintenance | Bug fixes and security patches |
| `v1.1.0+` | Extensions | Backward-compatible features |

Roadmap versions are targets, not commitments. Release scope can change based on evaluation and actual needs.

## 9. Open design questions

- What is the minimal evidence-reference schema for verified observations?
- How should the harness respond to insufficient evidence: report uncertainty, retry, or ask for logs?
- What iteration/token budgets produce useful results at acceptable cost?
- How should tests measure diagnosis quality versus mere schema compliance?
- When do repository scale and performance justify ripgrep or indexing?

## 10. Documentation and change policy

- Update this document when architecture, tool contracts, safety rules, or release scope changes.
- Update README when user-visible functionality, setup, or usage changes.
- Record notable changes under `CHANGELOG.md` **Unreleased**; move them under a version heading when a release is tagged.
- Prefer feature-oriented commits (`feat`, `fix`, `test`, `docs`, `refactor`, `chore`) and meaningful pull requests or commit messages.
- Never mark planned work as implemented solely because code has been drafted.
