import pytest
from src.editorial_pipeline.pipeline import PipelineContext
from src.editorial_pipeline.steps.pre_desk_review import PreDeskReviewStep

def test_pre_desk_review_sets_recommendation():
    step = PreDeskReviewStep()
    ctx = PipelineContext(manuscript_path="samples/test.docx")
    ctx.data["manuscript"] = {"title": "Test", "abstract": "Test abstract", "full_text": ""}
    ctx = step.run(ctx)
    assert ctx.recommendation in ["accept", "revisions", "reject"]
