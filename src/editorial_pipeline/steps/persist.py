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
