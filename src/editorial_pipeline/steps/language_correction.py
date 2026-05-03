from src.editorial_pipeline.pipeline import PipelineStep, PipelineContext

class LanguageCorrectionStep(PipelineStep):
    name = "language_correction"

    def should_run(self, ctx: PipelineContext) -> bool:
        return ctx.recommendation == "revisions"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        # TODO: LLM language correction
        ctx.data["corrected_text"] = ctx.data["manuscript"]["full_text"]
        return ctx
