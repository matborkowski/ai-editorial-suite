import logging
from src.editorial_pipeline.pipeline import PipelineStep, PipelineContext
from src.editorial_pipeline.rag.reviewer_store import ReviewerStore

log = logging.getLogger(__name__)

class ReviewerRecommendationStep(PipelineStep):
    name = "reviewer_recommendation"

    def __init__(
        self,
        profiles_path: str = "data/reviewers_profiles.csv",
        chroma_dir: str = "data/chroma_db",
        top_n: int = 5,
    ):
        self.top_n = top_n
        self.store = ReviewerStore(
            profiles_path=profiles_path,
            chroma_dir=chroma_dir,
        )

    def should_run(self, ctx: PipelineContext) -> bool:
        return ctx.recommendation != "reject"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        manuscript = ctx.data["manuscript"]

        # budujemy query z tytułu + abstraktu — to daje najlepsze wyniki semantyczne
        query = f"{manuscript.get('title', '')} {manuscript.get('abstract', '')}"

        log.info(f"Searching for top {self.top_n} reviewers...")
        reviewers = self.store.search(query=query, top_n=self.top_n)

        ctx.data["reviewers"] = reviewers
        log.info(f"Found {len(reviewers)} reviewers")

        for i, r in enumerate(reviewers, 1):
            log.info(f"  {i}. {r['author']} | {r['topics']} | score: {r['score']:.3f}")

        return ctx