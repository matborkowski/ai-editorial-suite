# src/main.py

from ingestion.docx_parser import extract_text_from_docx
from extraction.issue_extractor import extract_issues
from engine.decision_engine import decide_stage1
from reporting.report_generator import generate_report


def run_pipeline(manuscript_path, ithenticate_data):
    print("=== Stage 1: Pre-Desk Review ===")

    # 1. Manuscript loading
    manuscript_text = extract_text_from_docx(manuscript_path)

    # 2. Issues search (LLM)
    issues = extract_issues(manuscript_text, ithenticate_data)

    # 3. Decision
    decision = decide_stage1({
        "issues": issues,
        "scope_fit": "high_fit",  # tymczasowo
        "similarity_risk": ithenticate_data.get("risk", "low"),
        "reproducibility": "partially_reproducible",  # tymczasowo
        "experimental_quality": "acceptable",  # tymczasowo
        "results_conclusions_consistency": "mostly_supported",  # tymczasowo
        "statistical_adequacy": "partially_adequate",  # tymczasowo
        "technical_compliance": "minor_deficiencies",  # tymczasowo
        "manuscript_file_status": "single_valid_docx",
        "title_match_with_ithenticate": True
    })

    # 4. Report
    report = generate_report(issues, decision)

    print("\n=== FINAL REPORT ===\n")
    print(report)

    return report


if __name__ == "__main__":
    manuscript_path = "examples/sample.docx"

    ithenticate_data = {
        "similarity_percent": 15,
        "risk": "low"
    }

    run_pipeline(manuscript_path, ithenticate_data)