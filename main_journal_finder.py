import argparse
import sys
from pathlib import Path

from src.journal_finder.stage1_filter import JournalFinderError, run_stage1
from src.journal_finder.stage2 import JournalFinderStage2Error, run_stage2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Journal Finder pipeline entrypoint")
    subparsers = parser.add_subparsers(dest="command", required=True)

    stage1_parser = subparsers.add_parser("stage1", help="Run Stage 1: filter journals from ministry list")
    stage1_parser.add_argument("--file", required=True, help="Path to ministry XLSX file")
    stage1_parser.add_argument("--sheet", default="Czasopisma _nauk", help="Worksheet name in XLSX")
    stage1_parser.add_argument("--disciplines", required=True, help="Disciplines separated by ';' or newline")
    stage1_parser.add_argument("--min-points", required=True, type=int, help="Minimum points")
    stage1_parser.add_argument("--max-points", required=True, type=int, help="Maximum points")
    stage1_parser.add_argument("--output-dir", default=".", help="Output directory")
    stage1_parser.add_argument("--max-rows-per-docx", type=int, default=700, help="Rows per Stage 1 DOCX part")
    stage1_parser.add_argument("--output-basename", default="JournalFinder_stage1_results", help="Base filename")

    stage2_parser = subparsers.add_parser("stage2", help="Run Stage 2 on Stage 1 DOCX output")
    stage2_parser.add_argument("--stage1-docx", required=True, nargs="+", help="One or more Stage 1 DOCX files")
    stage2_parser.add_argument("--article-title", required=True, help="Article title")
    stage2_parser.add_argument("--abstract", default=None, help="Abstract text")
    stage2_parser.add_argument("--abstract-file", default=None, help="Path to abstract TXT file")
    stage2_parser.add_argument("--keywords", required=True, help="Keywords separated by ';', ',' or newline")
    stage2_parser.add_argument("--metadata-csv", default=None, help="Optional metadata CSV")
    stage2_parser.add_argument("--enable-web", action="store_true", help="Enable web profile scraping")
    stage2_parser.add_argument("--use-openalex-discovery", action="store_true", help="Discover homepage via OpenAlex")
    stage2_parser.add_argument("--output-dir", default=".", help="Output directory")
    stage2_parser.add_argument("--output-file", default=None, help="Output DOCX filename")
    stage2_parser.add_argument("--top-n", type=int, default=3, help="Top journals in summary section")
    stage2_parser.add_argument("--max-journals", type=int, default=None, help="Optional processing limit")
    stage2_parser.add_argument("--web-delay", type=float, default=0.5, help="Delay between HTTP requests")

    pipeline_parser = subparsers.add_parser("pipeline", help="Run Stage 1 and Stage 2 in one command")
    pipeline_parser.add_argument("--file", required=True, help="Path to ministry XLSX file")
    pipeline_parser.add_argument("--sheet", default="Czasopisma _nauk", help="Worksheet name in XLSX")
    pipeline_parser.add_argument("--disciplines", required=True, help="Disciplines separated by ';' or newline")
    pipeline_parser.add_argument("--min-points", required=True, type=int, help="Minimum points")
    pipeline_parser.add_argument("--max-points", required=True, type=int, help="Maximum points")
    pipeline_parser.add_argument("--stage1-output-dir", default=".", help="Output directory for Stage 1")
    pipeline_parser.add_argument("--max-rows-per-docx", type=int, default=700, help="Rows per Stage 1 DOCX part")
    pipeline_parser.add_argument("--stage1-output-basename", default="JournalFinder_stage1_results", help="Base filename")
    pipeline_parser.add_argument("--article-title", required=True, help="Article title")
    pipeline_parser.add_argument("--abstract", default=None, help="Abstract text")
    pipeline_parser.add_argument("--abstract-file", default=None, help="Path to abstract TXT file")
    pipeline_parser.add_argument("--keywords", required=True, help="Keywords separated by ';', ',' or newline")
    pipeline_parser.add_argument("--metadata-csv", default=None, help="Optional metadata CSV")
    pipeline_parser.add_argument("--enable-web", action="store_true", help="Enable web profile scraping")
    pipeline_parser.add_argument("--use-openalex-discovery", action="store_true", help="Discover homepage via OpenAlex")
    pipeline_parser.add_argument("--stage2-output-dir", default=".", help="Output directory for Stage 2")
    pipeline_parser.add_argument("--output-file", default=None, help="Output DOCX filename")
    pipeline_parser.add_argument("--top-n", type=int, default=3, help="Top journals in summary section")
    pipeline_parser.add_argument("--max-journals", type=int, default=None, help="Optional processing limit")
    pipeline_parser.add_argument("--web-delay", type=float, default=0.5, help="Delay between HTTP requests")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "stage1":
            output_paths, total_count, _ = run_stage1(
                file_path=args.file,
                sheet_name=args.sheet,
                disciplines_raw=args.disciplines,
                min_points=args.min_points,
                max_points=args.max_points,
                output_dir=args.output_dir,
                max_rows_per_docx=args.max_rows_per_docx,
                output_basename=args.output_basename,
            )
            if not output_paths:
                print("Brak czasopism spełniających podane kryteria. Nie wygenerowano DOCX.")
                return 0
            print(f"Znaleziono czasopism: {total_count}")
            print("Wygenerowano pliki DOCX:")
            for path in output_paths:
                print(f"- {path}")
            return 0

        if args.command == "stage2":
            output_path, sorted_candidates = run_stage2(
                stage1_docx_paths=args.stage1_docx,
                article_title=args.article_title,
                abstract=args.abstract,
                abstract_file=args.abstract_file,
                keywords_raw=args.keywords,
                metadata_csv=args.metadata_csv,
                enable_web=args.enable_web,
                use_openalex_discovery=args.use_openalex_discovery,
                output_dir=args.output_dir,
                output_file=args.output_file,
                top_n=args.top_n,
                max_journals=args.max_journals,
                web_delay=args.web_delay,
            )
            print(f"Przeanalizowano czasopism: {len(sorted_candidates)}")
            print(f"Wygenerowano DOCX: {output_path}")
            print("Najlepsze dopasowania:")
            for idx, candidate in enumerate(sorted_candidates[: args.top_n], start=1):
                print(f"{idx}. {candidate.title} — {candidate.score}/10")
            return 0

        stage1_docx_paths, total_count, _ = run_stage1(
            file_path=args.file,
            sheet_name=args.sheet,
            disciplines_raw=args.disciplines,
            min_points=args.min_points,
            max_points=args.max_points,
            output_dir=args.stage1_output_dir,
            max_rows_per_docx=args.max_rows_per_docx,
            output_basename=args.stage1_output_basename,
        )
        if not stage1_docx_paths:
            print("Brak czasopism spełniających podane kryteria w Stage 1. Pipeline zatrzymany.")
            return 0

        print(f"Stage 1 zakończony. Znaleziono czasopism: {total_count}")
        print("Pliki Stage 1:")
        for path in stage1_docx_paths:
            print(f"- {path}")

        output_path, sorted_candidates = run_stage2(
            stage1_docx_paths=[str(path) for path in stage1_docx_paths],
            article_title=args.article_title,
            abstract=args.abstract,
            abstract_file=args.abstract_file,
            keywords_raw=args.keywords,
            metadata_csv=args.metadata_csv,
            enable_web=args.enable_web,
            use_openalex_discovery=args.use_openalex_discovery,
            output_dir=args.stage2_output_dir,
            output_file=args.output_file,
            top_n=args.top_n,
            max_journals=args.max_journals,
            web_delay=args.web_delay,
        )
        print(f"Stage 2 zakończony. Wygenerowano DOCX: {output_path}")
        print("Najlepsze dopasowania:")
        for idx, candidate in enumerate(sorted_candidates[: args.top_n], start=1):
            print(f"{idx}. {candidate.title} — {candidate.score}/10")
        return 0
    except (JournalFinderError, JournalFinderStage2Error) as exc:
        print(f"Błąd: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nPrzerwano działanie programu.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
