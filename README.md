# AI Editorial Suite

AI Editorial Suite is a Python project for academic publishing workflows with two CLI products:

- `Editorial Pipeline` for editors (manuscript triage and reviewer support)
- `Journal Finder` for authors (Stage 1 filtering + Stage 2 ranking)

The codebase is functional but still in active development.

## Current Product Scope

### 1) Editorial Pipeline (editor-facing)

Input: manuscript `.docx`  
Output: JSON report and optional corrected manuscript text

Implemented flow:

1. `IngestionStep` parses manuscript content.
2. `PreDeskReviewStep` runs LLM pre-desk evaluation.
3. `ReviewerRecommendationStep` runs semantic retrieval of reviewers (skipped on reject).
4. `LanguageCorrectionStep` runs only for revisions.
5. `PersistStep` writes outputs.

Entrypoint: `main_editorial.py`

### 2) Journal Finder (author-facing)

Input: ministry journal list + article metadata  
Output: Stage 1 filtered journals and Stage 2 ranked journal recommendations (DOCX)

Implemented modes in one CLI:

- `stage1` - discipline + points filtering from XLSX, exports one or more DOCX files
- `stage2` - reads Stage 1 DOCX files, enriches metadata/web profiles, scores fit, exports DOCX report
- `pipeline` - executes Stage 1 -> Stage 2 in one command

Entrypoint: `main_journal_finder.py`

## Repository Structure

```text
ai-editorial-suite/
├── main_editorial.py
├── main_journal_finder.py
├── requirements.txt
├── src/
│   ├── ingestion/
│   │   └── docx_parser.py
│   ├── editorial_pipeline/
│   │   ├── config/
│   │   │   └── journal_config.json
│   │   ├── rag/
│   │   │   └── reviewer_store.py
│   │   ├── steps/
│   │   │   ├── ingestion.py
│   │   │   ├── pre_desk_review.py
│   │   │   ├── reviewer_recommendation.py
│   │   │   ├── language_correction.py
│   │   │   └── persist.py
│   │   ├── models.py
│   │   └── pipeline.py
│   └── journal_finder/
│       ├── stage1_filter.py
│       ├── stage2.py
│       ├── stage2_requirements.txt
│       ├── journal_finder_stage2_metadata_template.csv
│       ├── finder.py
│       └── models.py
├── data/
├── samples/
├── outputs/
└── tests/
```

## Installation

Use Python 3.11+.

```bash
pip install -r requirements.txt
pip install -r src/journal_finder/stage2_requirements.txt
```

Notes:

- `requirements.txt` covers core editorial pipeline stack.
- `stage2_requirements.txt` adds Stage 2 dependencies (`requests`, `beautifulsoup4`, `scikit-learn`, `python-docx`).

## Configuration

Set API key for editorial LLM steps:

```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "your_key_here"
```

Editorial config file:

- `src/editorial_pipeline/config/journal_config.json`

## Usage

### Editorial Pipeline

```bash
python main_editorial.py --path "samples/test_article_1.docx"
```

### Journal Finder - Stage 1

```bash
python main_journal_finder.py stage1 ^
  --file "Wykaz czasopism naukowych 2024.xlsx" ^
  --disciplines "nauki chemiczne; inżynieria chemiczna" ^
  --min-points 70 ^
  --max-points 140 ^
  --output-dir "outputs"
```

### Journal Finder - Stage 2

```bash
python main_journal_finder.py stage2 ^
  --stage1-docx "outputs/JournalFinder_stage1_results.docx" ^
  --article-title "Example manuscript title" ^
  --abstract-file "samples/abstract.txt" ^
  --keywords "electrochemistry; catalysis; membrane" ^
  --metadata-csv "src/journal_finder/journal_finder_stage2_metadata_template.csv" ^
  --output-dir "outputs"
```

### Journal Finder - Full Pipeline

```bash
python main_journal_finder.py pipeline ^
  --file "Wykaz czasopism naukowych 2024.xlsx" ^
  --disciplines "nauki chemiczne; inżynieria chemiczna" ^
  --min-points 70 ^
  --max-points 140 ^
  --article-title "Example manuscript title" ^
  --abstract-file "samples/abstract.txt" ^
  --keywords "electrochemistry; catalysis; membrane" ^
  --metadata-csv "src/journal_finder/journal_finder_stage2_metadata_template.csv" ^
  --stage1-output-dir "outputs" ^
  --stage2-output-dir "outputs"
```

To allow Stage 2 web enrichment, add:

- `--enable-web`
- optional: `--use-openalex-discovery`

## Current Limitations

- `src/journal_finder/finder.py` remains a legacy placeholder and is not the main path.
- Test coverage is still partial; some tests are placeholders.
- Reliability and observability are basic (no full retry/metrics framework yet).

## Roadmap (Next Priorities)

1. Increase automated test coverage for Stage 1/Stage 2 and pipeline integration.
2. Consolidate dependency management (single source of truth for requirements).
3. Harden LLM/network reliability (timeouts, retries, structured error taxonomy).
4. Improve data contracts and validation between steps.
5. Add CI checks (tests, linting, type checks).

## License

No license file is currently included in this repository.