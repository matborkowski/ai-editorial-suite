# AI Editorial Suite

> An AI-powered editorial workflow system for academic journals — built with Python and LLMs.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![LLM](https://img.shields.io/badge/LLM-powered-teal)
![Products](https://img.shields.io/badge/products-2-orange)
![Status](https://img.shields.io/badge/status-in%20development-yellow)

---

## What Changed in v2.0

The original plan treated four modules as equal, independent components — without defining who uses them or in what order. After a domain review, it became clear the project consists of **two separate products for two different users**.

| ❌ Old Plan | ✅ New Plan |
|---|---|
| 4 modules with no defined sequence | 2 products with clear step sequences |
| No defined actor (who uses this?) | Editor → Pipeline / Author → Journal Finder |
| Journal Finder mixed into the editorial pipeline | Journal Finder as a separate standalone CLI tool |
| No conditional logic between steps | Decision logic: `reject` / `revisions` / `accept` |

---

## Product 1: Editorial Pipeline

**User:** Journal editor  
**Input:** Full manuscript (`.docx`)  
**Output:** Editorial report with recommendation, reviewer list, and language corrections

### Pipeline Steps

```
Manuscript (.docx)
       │
       ▼
┌─────────────────┐
│  Step 1         │  Ingestion
│  docx_parser    │  → extracts title, abstract, keywords, sections, full text
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Step 2         │  Pre-Desk Review
│  LLM + Pydantic │  → scope check, statistics, similarity, compliance
└────────┬────────┘
         │
    ┌────┴─────────────────┐
    │                      │
  reject                revisions / accept
    │                      │
    ▼                      ▼
Stop + report     ┌─────────────────┐
                  │  Step 3         │  Reviewer Recommendation
                  │  RAG + Chroma   │  → embeddings, conflict filter, top-N
                  └────────┬────────┘
                           │
                    ┌──────┴──────────────┐
                    │                     │
                 revisions             accept
                    │                     │
                    ▼                     ▼
          ┌─────────────────┐      Skip this step
          │  Step 4         │  Language Correction
          │  LLM            │  → grammar, academic tone, clarity
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  Step 5         │  Persist
          │  JSON / PDF     │  → final report saved to outputs/
          └─────────────────┘
```

### Step Details

**Step 1 — Ingestion**  
Parses the `.docx` file and extracts: title, abstract, keywords, sections, full text.  
Returns a `ManuscriptData` Pydantic model.

**Step 2 — Pre-Desk Review**  
LLM evaluates journal scope compliance, topic fit, statistical quality, and similarity to existing work.  
Returns a `ReviewResult` with `recommendation: "accept" | "revisions" | "reject"`.  
If `reject` → pipeline stops here and generates a rejection report.

**Step 3 — Reviewer Recommendation** *(skipped on `reject`)*  
RAG pipeline compares manuscript embeddings against a reviewer profile database.  
Applies filters: conflicts of interest, availability, prior reviews.  
Returns top-N reviewers with justification.

**Step 4 — Language Correction** *(only on `revisions`)*  
LLM corrects grammar, academic tone, and clarity.  
Returns corrected text with annotated changes.

**Step 5 — Persist**  
Saves the final report to JSON (and optionally PDF).  
Report includes: recommendation, reviewer list, corrected text, error log.

---

## Product 2: Journal Finder

**User:** Academic author  
**Input:** Abstract or short description *(full manuscript not required)*  
**Output:** Ranked list of suitable journals with match justification

### Why a Separate Product?

Journal Finder operates at a different point in time — the author looks for a journal *before* submitting, while the editor receives the manuscript *after* that decision. These are fundamentally different tools:

| | Editorial Pipeline | Journal Finder |
|---|---|---|
| User | Journal editor | Academic author |
| Trigger | Manuscript received | Before submission |
| Input | Full `.docx` manuscript | Abstract only |
| Output | Editorial report | Journal ranking |
| Database | Reviewer profiles | Journal profiles |

---

## Project Structure

```
ai-editorial-suite/
├── src/
│   ├── ingestion/                  # shared parser — used by both products
│   │   └── docx_parser.py
│   ├── editorial_pipeline/         # Product 1: user = editor
│   │   ├── pipeline.py             # PipelineRunner + PipelineContext
│   │   ├── models.py               # ManuscriptData, ReviewResult (Pydantic)
│   │   ├── config/
│   │   │   └── journal_config.json # per-journal configuration
│   │   └── steps/
│   │       ├── ingestion.py
│   │       ├── pre_desk_review.py
│   │       ├── reviewer_recommendation.py
│   │       ├── language_correction.py
│   │       └── persist.py
│   └── journal_finder/             # Product 2: user = author
│       ├── finder.py
│       └── models.py
├── main_editorial.py               # CLI entrypoint for editors
├── main_journal_finder.py          # CLI entrypoint for authors
├── samples/
├── outputs/
├── tests/
│   ├── test_ingestion.py
│   ├── test_review.py
│   └── test_journal_finder.py
└── requirements.txt
```

---

## Requirements

```txt
# Parsing
python-docx>=1.1.0

# LLM
openai>=1.30.0
anthropic>=0.25.0

# Structured outputs
pydantic>=2.7.0

# RAG / Embeddings
chromadb>=0.5.0
sentence-transformers>=3.0.0

# Utilities
python-dotenv>=1.0.0
loguru>=0.7.0

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/matborkowski/ai-editorial-suite
cd ai-editorial-suite

# Install dependencies
pip install -r requirements.txt

# Run the editorial pipeline
python main_editorial.py --path samples/test_article_1.docx

# Run the journal finder
python main_journal_finder.py --abstract "your abstract text here"
```

---

## Implementation Roadmap

| Stage | Description | Status |
|---|---|---|
| 1 | Ingestion + Pydantic models (`ManuscriptData`, `ReviewResult`) | 🔄 In progress |
| 2 | Pre-Desk Review with real LLM + structured output | ⏳ Planned |
| 3 | Pipeline runner with conditional logic (reject/revisions/accept) | ⏳ Planned |
| 4 | Reviewer Recommendation — RAG + Chroma + embeddings | ⏳ Planned |
| 5 | Language Correction step | ⏳ Planned |
| 6 | Journal Finder as standalone CLI | ⏳ Planned |
| 7 | Unit tests for each pipeline step | ⏳ Planned |

---

## Architecture Principles

- **Domain-driven design** — structure reflects the real editorial workflow, not just a list of features
- **Pipeline pattern** — each step is an independent `PipelineStep` class, testable in isolation
- **Conditional execution** — steps run only when appropriate (`should_run()` per step)
- **Pydantic everywhere** — all data passed between steps is validated and typed
- **Config-driven** — journal-specific rules live in `journal_config.json`, not in code

---

*AI Editorial Suite — v2.0 — Architecture updated after domain review*