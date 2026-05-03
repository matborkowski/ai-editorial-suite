from src.ingestion.docx_parser import extract_manuscript, extract_paragraphs


def main():
    manuscript_path = "samples/test_article_1.docx"

    data = extract_manuscript(manuscript_path)

    print("\n=== TITLE ===")
    print(data["title"])

    print("\n=== ABSTRACT ===")
    print(data["abstract"][:500])

    print("\n=== SECTIONS ===")
    for section, content in data["sections"].items():
        print(f"\n--- {section.upper()} ---")
        print(content[:500])

    print("\n=== FULL TEXT LENGTH ===")
    print(len(data["full_text"]))

    print("\n=== KEYWORDS ===")
    print(data["keywords"])


if __name__ == "__main__":
    main()