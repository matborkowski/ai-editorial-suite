from pydantic import BaseModel, Field
from typing import Literal

class ManuscriptData(BaseModel):
    title: str
    abstract: str
    keywords: list[str]
    sections: dict[str, str]
    full_text: str

class ScopeAssessment(BaseModel):
    compliant: bool
    reason: str

class StatisticsAssessment(BaseModel):
    adequate: bool
    issues: list[str] = Field(default_factory=list)

class ReviewResult(BaseModel):
    recommendation: Literal["accept", "revisions", "reject"]
    scope: ScopeAssessment
    statistics: StatisticsAssessment
    language_quality: Literal["good", "acceptable", "poor"]
    major_issues: list[str] = Field(default_factory=list)
    minor_issues: list[str] = Field(default_factory=list)
    summary: str