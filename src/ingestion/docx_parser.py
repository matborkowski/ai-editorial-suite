# src/ingestion/docx_parser.py

import re
from pathlib import Path
from typing import Dict, List, Optional

from docx import Document


SECTION_ALIASES: Dict[str, List[str]] = {
    "abstract": [
        "abstract"
    ],
    "keywords": [
        "keywords",
        "key words"
    ],
    "introduction": [
        "introduction"
    ],
    "methods": [
        "materials and methods",
        "methodology",
        "methods",
        "experimental",
        "experimental part"
    ],
    "results": [
        "results"
    ],
    "discussion": [
        "discussion"
    ],
    "results_and_discussion": [
        "results and discussion",
        "results & discussion"
    ],
    "conclusions": [
        "conclusion",
        "conclusions",
        "summary"
    ],
    "references": [
        "references",
        "bibliography"
    ]
}


DEFAULT_SECTIONS = [
    "abstract",
    "keywords",
    "introduction",
    "methods",
    "results",
    "discussion",
    "conclusions",
    "references"
]


def normalize_text(text: str) -> str:
    """
    Normalize text for reliable comparison.
    """
    text = text.strip().lower()
    text = re.sub(r"^\d+(\.\d+)*\.?\s+", "", text)
    text = re.sub(r"[^a-zA-Z\s&]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_section_name(text: str) -> Optional[str]:
    """
    Match a paragraph text against known section headings.
    """
    normalized = normalize_text(text)

    for section_name, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if normalized == alias:
                return section_name

    return None


def extract_paragraphs(docx_path: str) -> List[str]:
    """
    Extract non-empty paragraphs from a DOCX file.
    """
    path = Path(docx_path)

    if not path.exists():
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")

    if path.suffix.lower() != ".docx":
        raise ValueError(f"Expected a .docx file, got: {path.suffix}")

    document = Document(docx_path)

    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return paragraphs


def extract_title(paragraphs: List[str]) -> str:
    """
    Extract a probable manuscript title.

    Current heuristic:
    - use the first non-empty paragraph
    - stop before standard metadata/section headings
    """
    if not paragraphs:
        return ""

    first_paragraph = paragraphs[0]

    if get_section_name(first_paragraph):
        return ""

    return first_paragraph

def extract_labeled_inline_section(paragraph: str) -> tuple[Optional[str], Optional[str]]:
    """
    Detect inline labeled sections such as:
    'Abstract: ...'
    'Keywords: ...'
    """
    patterns = {
        "abstract": r"^abstract\s*:\s*(.+)$",
        "keywords": r"^(keywords|key words)\s*:\s*(.+)$"
    }

    for section_name, pattern in patterns.items():
        match = re.match(pattern, paragraph.strip(), flags=re.IGNORECASE)
        if match:
            return section_name, match.group(match.lastindex).strip()

    return None, None

def extract_sections(paragraphs: List[str]) -> Dict[str, str]:
    """
    Extract manuscript sections using heading aliases.

    The parser scans paragraphs sequentially. When it detects a known section
    heading, all following paragraphs are assigned to that section until another
    known section heading is found.
    """
    sections = {section: "" for section in DEFAULT_SECTIONS}
    current_section: Optional[str] = None

    for paragraph in paragraphs:
        detected_section = get_section_name(paragraph)

        if detected_section:
            if detected_section == "results_and_discussion":
                current_section = "results"
            else:
                current_section = detected_section
            continue

        if current_section:
            sections[current_section] += paragraph + "\n"

    return {section: content.strip() for section, content in sections.items()}

def extract_sections(paragraphs: List[str]) -> Dict[str, str]:
    sections = {section: "" for section in DEFAULT_SECTIONS}
    current_section: Optional[str] = None

    for paragraph in paragraphs:
        inline_section, inline_content = extract_labeled_inline_section(paragraph)

        if inline_section:
            sections[inline_section] += inline_content + "\n"
            current_section = inline_section
            continue

        detected_section = get_section_name(paragraph)

        if detected_section:
            if detected_section == "results_and_discussion":
                current_section = "results"
            else:
                current_section = detected_section
            continue

        if current_section:
            sections[current_section] += paragraph + "\n"

    return {section: content.strip() for section, content in sections.items()}

def extract_manuscript(docx_path: str) -> Dict[str, object]:
    """
    Parse a DOCX manuscript into structured text fields.
    """
    paragraphs = extract_paragraphs(docx_path)
    sections = extract_sections(paragraphs)

    return {
        "title": extract_title(paragraphs),
        "abstract": sections.get("abstract", ""),
        "keywords": sections.get("keywords", ""),
        "sections": {
            "introduction": sections.get("introduction", ""),
            "methods": sections.get("methods", ""),
            "results": sections.get("results", ""),
            "discussion": sections.get("discussion", ""),
            "conclusions": sections.get("conclusions", ""),
            "references": sections.get("references", "")
        },
        "full_text": "\n".join(paragraphs)
    }