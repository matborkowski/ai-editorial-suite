from src.editorial_pipeline.pipeline import PipelineStep, PipelineContext
from src.ingestion.docx_parser import extract_manuscript

class IngestionStep(PipelineStep):
    name = "ingestion"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        ctx.data["manuscript"] = extract_manuscript(ctx.manuscript_path)
        return ctx
