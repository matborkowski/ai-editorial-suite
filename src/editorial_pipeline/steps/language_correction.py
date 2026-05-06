import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

from src.editorial_pipeline.pipeline import PipelineStep, PipelineContext

load_dotenv()
log = logging.getLogger(__name__)

# SECTIONS THAT DO NOT REQUIRE CORRECTIONS
SKIP_SECTIONS = {
    "references", "bibliography", "acknowledgments",
    "acknowledgements", "funding", "keywords",
}

SYSTEM_PROMPT = """You are an expert academic language editor specializing in scientific manuscripts.
Your task is to perform SOFT language correction only.

SOFT CORRECTION RULES:
- Correct grammar and syntax errors
- Improve clarity and readability where clearly needed
- Normalize academic tone (avoid informal language)
- Preserve all technical and scientific terminology exactly as written
- Do NOT restructure sentences unless grammar requires it
- Do NOT change meaning, interpretation, or factual content
- Do NOT expand or reduce content
- Do NOT optimize for any specific journal style

STRICT PRESERVATION RULES — NEVER modify these:
- Figure captions (e.g. "Figure 1.", "Fig. 2.")
- Table captions (e.g. "Table 1.")
- In-text references to figures and tables
- Placeholders: [FIGURE N], [TABLE N], [Figure N here], <Figure N>
- Citations and reference markers (e.g. [1], (Smith, 2020))
- Chemical formulas, equations, units of measurement
- Statistical values and numerical data

When you encounter a placeholder or caption — copy it VERBATIM and continue.

QUALITY PRINCIPLE:
When in doubt, preserve meaning over stylistic improvement.
Clarity must never come at the cost of semantic fidelity.

Return ONLY the corrected text. No explanations, no comments, no preamble."""


def _should_skip(section_name: str) -> bool:
    return section_name.strip().lower().rstrip(".") in SKIP_SECTIONS


def correct_section(client: OpenAI, section_name: str, text: str, context: str) -> str:
    """
    Correct a single section with global context (title + abstract).
    Context helps the model preserve domain-specific terminology.
    """
    user_prompt = f"""MANUSCRIPT CONTEXT (for terminology reference only — do not edit):
{context}

---
SECTION TO CORRECT: {section_name}

{text}
---

Apply soft language correction to the section above.
Return only the corrected section text."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,   
        max_tokens=4000,
    )

    return response.choices[0].message.content.strip()


class LanguageCorrectionStep(PipelineStep):
    name = "language_correction"

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def should_run(self, ctx: PipelineContext) -> bool:
        return ctx.recommendation == "revisions"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        manuscript = ctx.data["manuscript"]
        sections = manuscript.get("sections", {})

        if not sections:
            log.warning("No sections found in manuscript — skipping language correction")
            return ctx

        # GLOBAL CONTEXT
        global_context = (
            f"Title: {manuscript.get('title', '')}\n\n"
            f"Abstract: {manuscript.get('abstract', '')}"
        )

        corrected_sections = {}
        skipped_sections = []

        for section_name, text in sections.items():
            if _should_skip(section_name):
                corrected_sections[section_name] = text
                skipped_sections.append(section_name)
                log.info(f"[SKIP] {section_name}")
                continue

            if not text.strip():
                corrected_sections[section_name] = text
                continue

            log.info(f"[CORRECTING] {section_name} ({len(text)} chars)")
            try:
                corrected = correct_section(
                    client=self.client,
                    section_name=section_name,
                    text=text,
                    context=global_context,
                )
                corrected_sections[section_name] = corrected
                log.info(f"[DONE] {section_name}")
            except Exception as e:
                log.error(f"[FAIL] {section_name}: {e}")
                corrected_sections[section_name] = text  # fallback: oryginał

        ctx.data["corrected_sections"] = corrected_sections
        ctx.data["skipped_sections"] = skipped_sections
        log.info(
            f"Language correction complete. "
            f"Corrected: {len(corrected_sections) - len(skipped_sections)} sections, "
            f"Skipped: {len(skipped_sections)} sections."
        )

        return ctx