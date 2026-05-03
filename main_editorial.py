import argparse
import json
import logging
from dotenv import load_dotenv

from src.editorial_pipeline.pipeline import PipelineRunner
from src.editorial_pipeline.steps.ingestion import IngestionStep
from src.editorial_pipeline.steps.pre_desk_review import PreDeskReviewStep
from src.editorial_pipeline.steps.reviewer_recommendation import ReviewerRecommendationStep
from src.editorial_pipeline.steps.language_correction import LanguageCorrectionStep
from src.editorial_pipeline.steps.persist import PersistStep

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def load_config(path: str = "src/editorial_pipeline/config/journal_config.json") -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="AI Editorial Pipeline")
    parser.add_argument("--path", required=True, help="Path to manuscript .docx file")
    parser.add_argument("--config", default="src/editorial_pipeline/config/journal_config.json")
    args = parser.parse_args()

    config = load_config(args.config)

    pipeline = PipelineRunner(steps=[
        IngestionStep(),
        PreDeskReviewStep(model="gpt-4o"),
        ReviewerRecommendationStep(),
        LanguageCorrectionStep(),
        PersistStep(output_dir="outputs"),
    ])

    ctx = pipeline.run(manuscript_path=args.path, config=config)

    print(f"\n{'='*40}")
    print(f"Recommendation : {ctx.recommendation.upper()}")
    print(f"Report saved to: {ctx.data.get('report_path', 'N/A')}")
    if ctx.errors:
        print(f"Errors         : {ctx.errors}")
    print(f"{'='*40}\n")

if __name__ == "__main__":
    main()