# DevLens

**Evidence-oriented AI agent for investigating backend API failures.**

DevLens helps developers investigate failed API requests by combining structured incident information with read-only source-code inspection. Its goal is to produce actionable investigation reports that clearly distinguish **observations**, **hypotheses**, and **next steps**.

> **Project status:** v0.1.0 functional MVP (release documentation prepared; Git tag and GitHub Release pending). The CLI agent has passed live investigation checks and a three-case evaluation run.

## Why DevLens?

An HTTP 500 response often reveals little about the underlying failure. Developers must locate relevant handlers, inspect code paths, correlate logs, and decide what to verify next. DevLens aims to accelerate this process without presenting unverified guesses as established facts.

## Capabilities and roadmap

| Capability | Status | Notes |
| --- | --- | --- |
| Structured investigation reports | Implemented | OpenAI Responses API + Pydantic |
| Business-rule validation | Implemented | Required observations and next steps |
| Automated unit tests | Implemented | 25 passing tests: 5 validation, 8 repository tools, 4 dispatch, 4 mocked agent-loop, 2 fixture, and 2 evaluation-summary tests |
| Read-only `search_code` / `read_file` | Implemented, unit tested | Repository-scoped Python source inspection |
| LLM function calling and bounded agent loop | Implemented, Tested | Allowlisted dispatcher; tool-call budget; sequential calls; Mock Integration Tests; Structured Tool Trace |
| CLI and sample bug fixture | Implemented, live E2E exercised | `run_investigation.py` and `examples/buggy_api/app.py` |
| Reproducible bug fixtures | Implemented | Three simulated API failure scenarios: missing user, incorrect total, and missing authorization. |
| Evaluation runner | Implemented | Runs investigation cases and saves structured JSON artifacts. |
| Evaluation summary | Implemented | Reports completion rate, report validity, tool success rate, and average tool calls. |
| Root cause evaluation | Manual | Diagnosis quality is currently reviewed against known root causes; automated accuracy scoring is not yet implemented. |
| HTTP API, persistence, deployment | Future | Added when justified by product requirements |

## Architecture (v0.1.0)

```text
API failure details + optional logs + repository path
                      |
                      v
                 CLI entrypoint
                      |
                      v
             Bounded agent harness
                /           \
               v             v
       OpenAI Responses   Read-only tools
             API         search_code / read_file
                \           /
                 v         v
              InvestigationReport
                      |
                      v
             Business validation
                      |
                      v
              Structured output
```

The CLI-driven model-to-tool-to-report flow has been exercised live on three simulated API failure cases. This does not establish accuracy on production incidents. See [Design](docs/design.md) for implementation boundaries and design decisions.

## Tech stack

- **Python 3.11+** — application and tool implementation
- **OpenAI Python SDK** — model interaction and structured outputs
- **Pydantic v2** — typed report schema
- **pytest** — automated tests
- **python-dotenv** — local configuration

The MVP intentionally avoids adding a database, frontend, or orchestration framework before they are needed.

## Getting started (Windows PowerShell)

Clone the repository and enter its root directory. Then:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a `.env` file using `.env.example` as a reference (if present), and set:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_supported_model
```

Never commit `.env` or API credentials. To verify your environment:

```powershell
python -m pip check
python -m pytest tests/ -v
```

To run the structured-report prototype (uses the API and may incur cost):

```powershell
python structured_report.py
```

To try the **experimental agent CLI** against the intentionally buggy example repository (uses the API and may incur cost):

```powershell
python run_investigation.py --repo examples/buggy_api --failure "GET /api/users/999 expected HTTP 404 but returned HTTP 500 with body: Internal Server Error"
```

The model-to-tool-to-report flow has been exercised live. The example is a simulated Python handler, not a running HTTP server. Reports are not independently evidence-verified.

### Running evaluations

Run all evaluation cases (uses the API and may incur cost):

```powershell
python -m evals.run_evals
```

Run a specific case:

```powershell
python -m evals.run_evals --case incorrect_total
```

Summarize a saved evaluation run:

```powershell
python -m evals.summarize evals/results/<result_file>.json
```

Evaluation results are stored locally in `evals/results/`. A recorded three-case run completed all cases with eight successful tool calls and valid reports. The current metrics measure execution reliability and report validity, **not** automated root-cause accuracy. The baseline result predates the final fixture-cleanup verification and should not be presented as a post-cleanup benchmark without a new artifact.

## Engineering principles

- **Evidence over confidence:** distinguish observed facts from possible causes.
- **Read-only by default:** no arbitrary shell execution or source-code mutation by the agent.
- **Bounded execution:** limit tool calls, file reads, and model output.
- **Validation in layers:** schema checks, business rules, and evidence verification serve different purposes.
- **Incremental complexity:** prefer a modular monolith and small interfaces before adopting infrastructure.

## Versioning and development history

DevLens uses [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

- `0.x.y`: evolving pre-stable releases
- `1.0.0`: first stable release after defined acceptance criteria are met
- Patch versions (`1.0.1`) fix bugs; minor versions (`1.1.0`) add backward-compatible features

See [CHANGELOG](CHANGELOG.md) for feature-based progress and release notes. Git commits document implementation-level changes; version tags identify tested releases.

## Project documentation

- [Design and architecture](docs/design.md)
- [Changelog](CHANGELOG.md)

## Current limitations

DevLens is an early-stage functional MVP. Its CLI has been exercised live, and mocked agent-loop tests and a small evaluation suite exist. Reports do **not independently verify a root cause** or enforce evidence references. The three fixtures are simulated Python handlers, not deployed HTTP endpoints; the evaluation does not establish statistical reliability or automated root-cause accuracy. Repository access is intended for trusted local code, not a hardened sandbox. Repeated real-model regression testing and stronger safety controls remain future work.

## License

No license has been selected yet. All rights are reserved unless a license is added.
