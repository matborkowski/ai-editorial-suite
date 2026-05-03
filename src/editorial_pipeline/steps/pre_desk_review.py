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
