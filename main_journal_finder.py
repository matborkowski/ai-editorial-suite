import argparse
from src.journal_finder.finder import JournalFinder

def main():
    parser = argparse.ArgumentParser(description="Find suitable journals for your manuscript")
    parser.add_argument("--abstract", required=True, help="Abstract text or path to .txt file")
    parser.add_argument("--top", type=int, default=5, help="Number of journal suggestions")
    args = parser.parse_args()

    finder = JournalFinder()
    results = finder.find(abstract=args.abstract, top_n=args.top)

    print(f"\nTop {args.top} journal matches:")
    for i, match in enumerate(results, 1):
        print(f"\n{i}. {match.journal_name} (score: {match.score:.2f})")
        print(f"   {match.justification}")

if __name__ == "__main__":
    main()
