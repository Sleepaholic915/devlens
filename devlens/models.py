from pydantic import BaseModel


class InvestigationReport(BaseModel):
    observations: list[str]
    hypotheses: list[str]
    next_steps: list[str]