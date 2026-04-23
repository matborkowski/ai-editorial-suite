# AI Editorial Suite

Concept and ongoing development of an AI-driven system for **scientific journal editorial workflows**.

The project focuses on automating key stages of manuscript handling using modular AI components.

---

## Overview

AI Editorial Suite is designed as a **multi-module system** supporting editorial decision-making, content quality, and submission routing.

The system is based on a **config-driven architecture**, allowing adaptation to different journals.

---

## Modules

### 1. Pre-Desk Review Engine (Stage 1)
Automated initial screening of manuscripts before peer review.

Scope:
- technical compliance checks
- scope alignment
- reproducibility assessment
- results vs. conclusions consistency
- statistical adequacy
- similarity analysis (iThenticate-aware)

Output:
- structured pre-review report
- editorial recommendation:
  - `accept`
  - `revisions`
  - `reject`

---

### 2. Language Correction Module (Stage 2)
AI-assisted improvement of manuscript language quality.

Scope:
- grammar and style correction
- academic tone adjustment
- clarity and readability improvement

---

### 3. Reviewer Recommendation Engine (RAG)
AI-based system for suggesting suitable peer reviewers.

Approach:
- semantic search (embeddings)
- similarity to manuscript topic
- filtering by expertise

---

### 4. Journal Finder Module
Tool for matching manuscripts to appropriate journals.

Scope:
- topic matching
- scope alignment
- potential submission recommendations

---

## Current Focus

Active development is currently focused on:

→ **Stage 1 – Pre-Desk Review Engine**

Other modules are planned and will be developed incrementally.

---

## Architecture (Concept)

- modular design
- separation of:
  - configuration (JSON)
  - decision logic
  - LLM-based extraction
- scalable to multiple journals

---

## Status

- architecture defined
- repository structure prepared
- Stage 1 logic designed
- implementation in progress

---

## Note

This repository does not contain real manuscript data or confidential editorial materials.

---

## Author

Mateusz Borkowski