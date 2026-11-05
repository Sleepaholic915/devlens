# DevLens — Living Design Document

**Status:** Draft · Day 2

## 1. Problem and goal
DevLens is an AI-assisted investigator for backend API test failures. Given a failed request (endpoint, expected and actual behavior, response, and later logs), it will inspect evidence and produce a structured diagnosis that distinguishes observations, hypotheses, and verification steps.

## 2. Scope
**Current (Day 2):** CLI-style proof of concept; one LLM call; Pydantic `InvestigationReport`; local validation exercises.

**Planned:** Read-only code search and bounded file inspection, a controlled agent loop, evidence references, tracing, tests, and evaluation against a non-agent baseline.

**Non-goals for now:** Autonomous code edits, arbitrary shell execution, microservices, sophisticated orchestration frameworks.

## 3. Architecture (planned, not yet implemented)
```text
CLI / future HTTP API
         |
Investigation service
         |
Agent loop / orchestration
      /       \
LLM adapter   Read-only code tools
         |
Structured InvestigationReport
         |
Validation and future persistence
```

Prefer a modular monolith: one deployable Python application with clear internal boundaries. Do not create modules before they are needed.

## 4. Current data contract
```python
from pydantic import BaseModel

class InvestigationReport(BaseModel):
    observations: list[str]
    hypotheses: list[str]
    next_steps: list[str]
```

- `observations`: facts supported by the provided input or retrieved evidence.
- `hypotheses`: possible explanations; may be empty when evidence is insufficient.
- `next_steps`: concrete actions to gather evidence or verify a hypothesis.

**Current business checks:** observations and next_steps must each contain at least one item. These checks are currently separate from the Pydantic schema.

**Limitation:** Structural validity and simple business checks do not establish factual correctness.

## 5. Request / investigation flow
1. Receive failure information.
2. Validate input (future typed request model).
3. Call the LLM with instructions and structured output schema.
4. Parse response into `InvestigationReport`.
5. Check completion, parsing, and business constraints.
6. Display report; later verify claims against evidence and store traces.

## 6. Design decisions and tradeoffs
| Decision | Why | Revisit when |
|---|---|---|
| Python | Fits LLM integration and source-code analysis | Another language offers a concrete advantage |
| OpenAI SDK directly | Minimal abstraction; learn API and agent mechanics | Multi-provider or advanced orchestration becomes necessary |
| Pydantic | Typed output and reusable validation | Requirements change significantly |
| Modular monolith | Simple local development and debugging | Independent scaling or deployment becomes necessary |
| No database yet | No persistent query requirement in current CLI | Investigation history and trace querying are implemented |
| No LangChain/LangGraph yet | Single-call structured output does not require it | Stateful workflows or checkpointing justify it |

## 7. Reliability and safety principles
- Separate observations, hypotheses, and next steps.
- Never present an unverified root cause as confirmed.
- Future code tools must be read-only, repository-scoped, and bounded.
- Bound tool calls, token usage, and execution time.
- Treat exception handling, response validation, and evaluation as distinct concerns.

## 8. Open questions
- How should each observation cite exact evidence (file/line, log excerpt, or request input)?
- Should validation failures trigger one repair attempt or return an explicit error?
- What should an insufficient-information report look like?
- Which real-world failure cases should form the evaluation dataset?

## 9. Implementation log
- **Day 1:** OpenAI Responses API basic call and token usage.
- **Day 2 Step 1:** Pydantic model validation and type coercion.
- **Day 2 Step 2:** `InvestigationReport` model and manual validation.
- **Day 2 Step 3:** `responses.parse(..., text_format=InvestigationReport)` succeeded; parsed object confirmed.
- **Day 2 Step 4:** Separate validator for nonempty observations and next steps; local tests passed.

*Update this document when an architectural decision changes, not after every line of code.*
