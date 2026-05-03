import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

from src.editorial_pipeline.pipeline import PipelineStep, PipelineContext
from src.editorial_pipeline.models import ReviewResult

load_dotenv()
log = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an experienced academic journal editor performing a pre-desk review.
Your task is to evaluate whether a manuscript meets basic editorial standards
before sending it to peer review.

Evaluate the manuscript on:
1. Scope compliance — does it fit the journal's topic areas?
2. Statistical adequacy — are methods and data analysis appropriate?
3. Language quality — is the academic English acceptable?
4. Major issues — fundamental problems that warrant rejection
5. Minor issues — problems that require revisions

Respond ONLY with a valid JSON object matching this exact schema:
{
  "recommendation": "accept" | "revisions" | "reject",
  "scope": {
    "compliant": true | false,
    "reason": "string"
  },
  "statistics": {
    "adequate": true | false,
    "issues": ["string"]
  },
  "language_quality": "good" | "acceptable" | "poor",
  "major_issues": ["string"],
  "minor_issues": ["string"],
  "summary": "string (2-3 sentences)"
}

Decision logic:
- "reject" if scope is not compliant OR more than 2 major issues
- "revisions" if scope is compliant but has minor/moderate issues
- "accept" if scope is compliant and no major issues
"""

def build_user_prompt(manuscript: dict, config: dict) -> str:
    journal_name = config.get("journal_name", "Unknown Journal")
    scope_keywords = ", ".join(config.get("scope_keywords", []))

    return f"""
Journal: {journal_name}
Journal scope keywords: {scope_keywords}

--- MANUSCRIPT ---
Title: {manuscript.get("title", "N/A")}

Abstract:
{manuscript.get("abstract", "N/A")}

Keywords: {", ".join(manuscript.get("keywords", []))}

Full text (truncated to 3000 chars):
{manuscript.get("full_text", "")[:3000]}
"""

class PreDeskReviewStep(PipelineStep):
    name = "pre_desk_review"

    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def run(self, ctx: PipelineContext) -> PipelineContext:
        manuscript = ctx.data["manuscript"]
        config = ctx.config

        log.info(f"Running pre-desk review for: {manuscript.get('title', 'Unknown')}")

        user_prompt = build_user_prompt(manuscript, config)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,      # niska temperatura = bardziej deterministyczne oceny
            max_tokens=1000,
            response_format={"type": "json_object"},  # wymusza JSON output
        )

        raw = response.choices[0].message.content
        parsed = json.loads(raw)
        result = ReviewResult(**parsed)   # walidacja Pydantic

        ctx.data["review"] = result.model_dump()
        ctx.recommendation = result.recommendation

        log.info(f"Review complete. Recommendation: {result.recommendation}")
        log.info(f"Summary: {result.summary}")

        return ctx