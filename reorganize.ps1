# AI Editorial Suite - Project Reorganization Script v2.0
# Run from the root of the project: .\reorganize.ps1

Write-Host "Starting project reorganization..." -ForegroundColor Cyan

# ─── CREATE NEW DIRECTORIES ───────────────────────────────────────────────
$dirs = @(
    "src\editorial_pipeline\steps",
    "src\editorial_pipeline\config",
    "src\journal_finder",
    "samples",
    "outputs",
    "tests"
)

foreach ($dir in $dirs) {
    if (-Not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  [+] Created $dir" -ForegroundColor Green
    } else {
        Write-Host "  [=] Already exists: $dir" -ForegroundColor Yellow
    }
}

# ─── MOVE main.py to root ─────────────────────────────────────────────────
if (Test-Path "src\main.py") {
    Move-Item "src\main.py" "main_editorial.py" -Force
    Write-Host "  [>] Moved src\main.py -> main_editorial.py" -ForegroundColor Green
}

# ─── CREATE NEW PYTHON FILES WITH BOILERPLATE ─────────────────────────────
$files = @{

    # ── editorial_pipeline ──────────────────────────────────────────────
    "src\editorial_pipeline\__init__.py" = ""

    "src\editorial_pipeline\models.py" = @"
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
"@

    "src\editorial_pipeline\pipeline.py" = @"
import logging
import time
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)

@dataclass
class PipelineContext:
    manuscript_path: str
    config: dict = field(default_factory=dict)
    data: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)
    recommendation: str = ""

class PipelineStep(ABC):
    name: str = "unnamed_step"

    @abstractmethod
    def run(self, ctx: PipelineContext) -> PipelineContext: ...

    def should_run(self, ctx: PipelineContext) -> bool:
        return True

class PipelineRunner:
    def __init__(self, steps: list[PipelineStep]):
        self.steps = steps

    def run(self, manuscript_path: str, config: dict = None) -> PipelineContext:
        ctx = PipelineContext(manuscript_path=manuscript_path, config=config or {})
        log.info(f"Pipeline start: {manuscript_path}")

        for step in self.steps:
            if not step.should_run(ctx):
                log.info(f"[SKIP] {step.name}")
                continue
            log.info(f"[RUN]  {step.name}")
            t0 = time.time()
            try:
                ctx = step.run(ctx)
            except Exception as e:
                log.error(f"[FAIL] {step.name}: {e}")
                ctx.errors.append({"step": step.name, "error": str(e)})
                break
            finally:
                log.info(f"[DONE] {step.name} ({time.time()-t0:.2f}s)")

        return ctx
"@

    "src\editorial_pipeline\config\journal_config.json" = @"
{
  "journal_name": "Example Journal of Science",
  "scope_keywords": ["machine learning", "neural networks", "AI"],
  "min_abstract_words": 150,
  "max_abstract_words": 300,
  "required_sections": ["introduction", "methods", "results", "conclusion"],
  "language": "english"
}
"@

    # ── steps ────────────────────────────────────────────────────────────
    "src\editorial_pipeline\steps\__init__.py" = ""

    "src\editorial_pipeline\steps\ingestion.py" = @"
from src.editorial_pipeline.pipeline import PipelineStep, PipelineContext
from src.ingestion.docx_parser import extract_manuscript

class IngestionStep(PipelineStep):
    name = "ingestion"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        ctx.data["manuscript"] = extract_manuscript(ctx.manuscript_path)
        return ctx
"@

    "src\editorial_pipeline\steps\pre_desk_review.py" = @"
from src.editorial_pipeline.pipeline import PipelineStep, PipelineContext

class PreDeskReviewStep(PipelineStep):
    name = "pre_desk_review"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        manuscript = ctx.data["manuscript"]
        # TODO: replace with real LLM call + Pydantic structured output
        result = {"recommendation": "revisions", "issues": [], "summary": ""}
        ctx.data["review"] = result
        ctx.recommendation = result["recommendation"]
        return ctx
"@

    "src\editorial_pipeline\steps\reviewer_recommendation.py" = @"
from src.editorial_pipeline.pipeline import PipelineStep, PipelineContext

class ReviewerRecommendationStep(PipelineStep):
    name = "reviewer_recommendation"

    def should_run(self, ctx: PipelineContext) -> bool:
        return ctx.recommendation != "reject"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        # TODO: RAG pipeline — embeddings + Chroma + conflict filter
        ctx.data["reviewers"] = []
        return ctx
"@

    "src\editorial_pipeline\steps\language_correction.py" = @"
from src.editorial_pipeline.pipeline import PipelineStep, PipelineContext

class LanguageCorrectionStep(PipelineStep):
    name = "language_correction"

    def should_run(self, ctx: PipelineContext) -> bool:
        return ctx.recommendation == "revisions"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        # TODO: LLM language correction
        ctx.data["corrected_text"] = ctx.data["manuscript"]["full_text"]
        return ctx
"@

    "src\editorial_pipeline\steps\persist.py" = @"
import json
from pathlib import Path
from src.editorial_pipeline.pipeline import PipelineStep, PipelineContext

class PersistStep(PipelineStep):
    name = "persist"

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def run(self, ctx: PipelineContext) -> PipelineContext:
        stem = Path(ctx.manuscript_path).stem
        out = self.output_dir / f"{stem}_report.json"
        report = {
            "manuscript": ctx.manuscript_path,
            "recommendation": ctx.recommendation,
            "review": ctx.data.get("review", {}),
            "reviewers": ctx.data.get("reviewers", []),
            "errors": ctx.errors,
        }
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        ctx.data["report_path"] = str(out)
        return ctx
"@

    # ── journal_finder ───────────────────────────────────────────────────
    "src\journal_finder\__init__.py" = ""

    "src\journal_finder\models.py" = @"
from pydantic import BaseModel

class JournalMatch(BaseModel):
    journal_name: str
    score: float
    justification: str
    url: str = ""
"@

    "src\journal_finder\finder.py" = @"
from src.journal_finder.models import JournalMatch

class JournalFinder:
    def find(self, abstract: str, top_n: int = 5) -> list[JournalMatch]:
        # TODO: embed abstract + compare against journal profiles database
        return []
"@

    # ── entrypoints ──────────────────────────────────────────────────────
    "main_journal_finder.py" = @"
import argparse
from src.journal_finder.finder import JournalFinder

def main():
    parser = argparse.ArgumentParser(description="Find suitable journals for your manuscript")
    parser.add_argument("--abstract", required=True, help="Abstract text or path to .txt file")
    parser.add_argument("--top", type=int, default=5, help="Number of journal suggestions")
    args = parser.parse_args()

    finder = JournalFinder()
    results = finder.find(abstract=args.abstract, top_n=args.top)

    print(f"\nTop {args.top} journal matches:")
    for i, match in enumerate(results, 1):
        print(f"\n{i}. {match.journal_name} (score: {match.score:.2f})")
        print(f"   {match.justification}")

if __name__ == "__main__":
    main()
"@

    # ── tests ─────────────────────────────────────────────────────────────
    "tests\__init__.py" = ""

    "tests\test_ingestion.py" = @"
import pytest
from src.ingestion.docx_parser import extract_manuscript

def test_extract_manuscript_returns_required_keys():
    # TODO: add a sample .docx to samples/ and point to it
    pass
"@

    "tests\test_review.py" = @"
import pytest
from src.editorial_pipeline.pipeline import PipelineContext
from src.editorial_pipeline.steps.pre_desk_review import PreDeskReviewStep

def test_pre_desk_review_sets_recommendation():
    step = PreDeskReviewStep()
    ctx = PipelineContext(manuscript_path="samples/test.docx")
    ctx.data["manuscript"] = {"title": "Test", "abstract": "Test abstract", "full_text": ""}
    ctx = step.run(ctx)
    assert ctx.recommendation in ["accept", "revisions", "reject"]
"@

    "tests\test_journal_finder.py" = @"
import pytest
from src.journal_finder.finder import JournalFinder

def test_journal_finder_returns_list():
    finder = JournalFinder()
    results = finder.find(abstract="This paper studies machine learning.")
    assert isinstance(results, list)
"@
}

foreach ($path in $files.Keys) {
    if (-Not (Test-Path $path)) {
        $content = $files[$path]
        Set-Content -Path $path -Value $content -Encoding UTF8
        Write-Host "  [+] Created $path" -ForegroundColor Green
    } else {
        Write-Host "  [=] Already exists (skipped): $path" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Done! New project structure:" -ForegroundColor Cyan
Get-ChildItem -Recurse -Filter "*.py" | Select-Object FullName | Sort-Object FullName
Write-Host ""
Write-Host "Next step: run the editorial pipeline with:" -ForegroundColor Cyan
Write-Host "  python main_editorial.py --path samples/test_article_1.docx" -ForegroundColor White
