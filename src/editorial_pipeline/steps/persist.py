import json
from pathlib import Path
from datetime import datetime
from src.editorial_pipeline.pipeline import PipelineStep, PipelineContext

class PersistStep(PipelineStep):
    name = "persist"

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def run(self, ctx: PipelineContext) -> PipelineContext:
        stem = Path(ctx.manuscript_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Main report — JSON
        report_path = self.output_dir / f"{stem}_report_{timestamp}.json"
        report = self._build_report(ctx)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        ctx.data["report_path"] = str(report_path)
        
        # Corrected manuscript — TXT (if language correction ran)
        if "corrected_sections" in ctx.data:
            corrected_path = self.output_dir / f"{stem}_corrected_{timestamp}.txt"
            corrected_text = self._build_corrected_manuscript(ctx)
            corrected_path.write_text(corrected_text, encoding="utf-8")
            ctx.data["corrected_path"] = str(corrected_path)
        
        return ctx

    def _build_report(self, ctx: PipelineContext) -> dict:
        """Build comprehensive editorial report."""
        manuscript = ctx.data.get("manuscript", {})
        review = ctx.data.get("review", {})
        reviewers = ctx.data.get("reviewers", [])
        
        report = {
            "metadata": {
                "manuscript_path": ctx.manuscript_path,
                "title": manuscript.get("title", "Unknown"),
                "processed_at": datetime.now().isoformat(),
                "recommendation": ctx.recommendation,
            },
            "pre_desk_review": review,
            "reviewers": reviewers,
            "errors": ctx.errors,
        }
        
        # Language correction summary
        if "corrected_sections" in ctx.data:
            report["language_correction"] = {
                "status": "completed",
                "sections_corrected": len(ctx.data["corrected_sections"]) - len(ctx.data.get("skipped_sections", [])),
                "sections_skipped": ctx.data.get("skipped_sections", []),
            }
        
        return report

    def _build_corrected_manuscript(self, ctx: PipelineContext) -> str:
        """Build human-readable corrected manuscript."""
        manuscript = ctx.data.get("manuscript", {})
        corrected_sections = ctx.data.get("corrected_sections", {})
        
        lines = []
        lines.append("=" * 80)
        lines.append(f"CORRECTED MANUSCRIPT: {manuscript.get('title', 'Untitled')}")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append("ABSTRACT")
        lines.append("-" * 80)
        lines.append(manuscript.get("abstract", "N/A"))
        lines.append("")
        
        if manuscript.get("keywords"):
            lines.append("KEYWORDS")
            lines.append("-" * 80)
            lines.append(", ".join(manuscript["keywords"]))
            lines.append("")
        
        for section_name, text in corrected_sections.items():
            lines.append(section_name.upper())
            lines.append("-" * 80)
            lines.append(text)
            lines.append("")
        
        return "\n".join(lines)