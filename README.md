# DevLens

**Evidence-oriented AI agent for investigating backend API failures.**

DevLens helps developers investigate failed API requests by combining structured incident information with read-only source-code inspection. Its goal is to produce actionable investigation reports that clearly distinguish **observations**, **hypotheses**, and **next steps**.

> **Project status:** Pre-MVP development. The first functional release is planned as **v0.1.0**. Features marked *Planned* are not yet implemented.

## Why DevLens?

An HTTP 500 response often reveals little about the underlying failure. Developers must locate relevant handlers, inspect code paths, correlate logs, and decide what to verify next. DevLens aims to accelerate this process without presenting unverified guesses as established facts.

## Capabilities and roadmap

| Capability | Status | Notes |
| --- | --- | --- |
| Structured investigation reports | Implemented | OpenAI Responses API + Pydantic |
| Business-rule validation | Implemented | Required observations and next steps |
| Unit tests for report validation | Implemented | pytest |
| Read-only `search_code` / `read_file` | In progress | Repository-scoped Python source inspection |
| LLM function calling and bounded agent loop | Planned for v0.1.0 | Explicit tool dispatch and execution limits |
| End-to-end CLI and reproducible bug fixtures | Planned for v0.1.0 | Demonstrable investigation workflow |
| Evidence attribution and evaluation suite | Planned | Trace claims to code/logs and benchmark cases |
| HTTP API, persistence, deployment | Future | Added when justified by product requirements |

## Architecture (target for v0.1.0)

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

The architecture above is a **target**, not a claim that the end-to-end loop is already working. See [Design](docs/design.md) for current implementation boundaries and design decisions.

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

To run the current structured-report prototype (uses the API and may incur cost):

```powershell
python structured_report.py
```

**Note:** The complete CLI agent is not available until the v0.1.0 milestone. Do not treat the prototype as an evidence-verified root-cause diagnosis.

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

DevLens is a development-stage prototype. Its current structured reports are generated from supplied failure details and **do not independently verify a root cause**. Code-inspection tools, agent orchestration, and evaluation are being integrated.

## License

No license has been selected yet. All rights are reserved unless a license is added.
