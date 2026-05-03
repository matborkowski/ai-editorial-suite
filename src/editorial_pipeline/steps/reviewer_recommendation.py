from src.editorial_pipeline.pipeline import PipelineStep, PipelineContext

class ReviewerRecommendationStep(PipelineStep):
    name = "reviewer_recommendation"

    def should_run(self, ctx: PipelineContext) -> bool:
        return ctx.recommendation != "reject"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        # TODO: RAG pipeline â€” embeddings + Chroma + conflict filter
        ctx.data["reviewers"] = []
        return ctx
