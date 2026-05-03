from pydantic import BaseModel, Field
from typing import Literal

class ManuscriptData(BaseModel):
    title: str
    abstract: str
    keywords: list[str]
    sections: dict[str, str]
    full_text: str

class ReviewResult(BaseModel):
    recommendation: Literal["accept", "revisions", "reject"]
    scope_compliance: bool
    issues: list[str] = Field(default_factory=list)
    summary: str
