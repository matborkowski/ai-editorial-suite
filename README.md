# AI Editorial Suite

**AI Editorial Suite** is an experimental Python toolkit for supporting editorial workflows in scholarly journals. Its current focus is the **Editorial Pipeline**: manuscript intake, preliminary editorial screening, reviewer suggestions and language correction.

**Status:** Prototype / under development. The software is not production-ready, and its AI outputs require independent editorial verification.

> **Looking for the Polish ministry journal search tool?** It is now developed independently in [Polish Journal Finder](https://github.com/matborkowski/polish-journal-finder). The legacy Journal Finder implementation has been removed from this repository.

## Current workflow

The command-line entry point is `main_editorial.py`.

| Step | Module | Function |
| --- | --- | --- |
| 1 | Manuscript ingestion | Extracts text and basic structure from DOCX manuscripts |
| 2 | Pre-desk review | Requests an LLM-based preliminary assessment of scope and editorial issues |
| 3 | Reviewer recommendation | Uses embeddings and a local Chroma database to find potentially relevant reviewers |
| 4 | Language correction | Applies conservative English-language corrections when revisions are recommended |
| 5 | Report generation | Saves a JSON report and, where applicable, corrected text in TXT format |

The modules are implemented, but end-to-end reliability and automated test coverage are limited. Recommendations must not be used as autonomous editorial decisions. Reviewer matches require checks for expertise, identity, conflicts of interest and availability.

## Project structure

```text
ai-editorial-suite/
├── main_editorial.py
├── requirements.txt
├── src/
│   ├── editorial_pipeline/
│   │   ├── config/journal_config.json
│   │   ├── rag/reviewer_store.py
│   │   ├── steps/
│   │   ├── models.py
│   │   └── pipeline.py
│   └── ingestion/docx_parser.py
├── data/reviewers_profiles.csv
├── scripts/build_reviewer_profiles.py
└── tests/
```

## Installation

A Python 3.11+ environment is recommended; newer interpreter versions have not been comprehensively tested.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set your OpenAI API key in the environment (do not commit API keys or unpublished manuscripts):

```powershell
$env:OPENAI_API_KEY = "your-api-key"
```

Configuration: `src/editorial_pipeline/config/journal_config.json`. The included settings are illustrative, not journal-specific production rules.

## Run

From the repository root:

```bash
python main_editorial.py --path "path/to/manuscript.docx"
```

The pipeline currently uses `gpt-4o` in its LLM steps; access and API charges may apply. Reviewer embeddings are generated locally with the configured sentence-transformers model. The first run may need to download that model. Output is written to `outputs/`.

Run the existing tests with:

```bash
python -m pytest -q
```

**Testing note:** Some current tests are placeholders or depend on an API key. A passing test suite is not yet evidence of production readiness.

## Known limitations

- The DOCX parser uses heuristics and may not faithfully recover complex article layouts, tables, references or figures.
- Pre-desk assessment relies on an LLM and can be inaccurate. It is not a substitute for expert editorial judgment.
- Reviewer matching is based on a limited local profile dataset; matches are not validated reviewer invitations.
- Language correction outputs plain text; it does not preserve the original DOCX formatting.
- Robust integration tests, reliable exception handling, data-validation policies and continuous integration are still needed.
- Unpublished manuscript content is sent to an external model API in LLM steps. Journal confidentiality rules and data-processing requirements must be addressed before using real submissions.

## Next priorities

1. Replace placeholder tests with meaningful ingestion and end-to-end tests.
2. Evaluate the DOCX parser and the quality of LLM assessments on controlled examples.
3. Improve reviewer-data quality and implement conflict-of-interest checks.
4. Add reproducible configuration, logging, validation and CI.
5. Design a human-in-the-loop editorial interface.

## License

MIT — see [LICENSE](LICENSE).

## Related project

[Polish Journal Finder](https://github.com/matborkowski/polish-journal-finder) — an independent tool for searching and comparing journals in Polish ministry lists.
