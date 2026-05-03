"""
build_reviewer_profiles.py

Aggregates raw publication-level reviewer data into reviewer profiles.
Input:  reviewers_summary_good.csv  (one row per publication)
Output: reviewers_profiles.csv      (one row per reviewer)

Usage:
    python build_reviewer_profiles.py
"""

import csv
from collections import defaultdict
from pathlib import Path

INPUT  = "/mnt/user-data/uploads/reviewers_summary_good.csv"
OUTPUT = "/mnt/user-data/outputs/reviewers_profiles.csv"

def load_raw(path: str) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = [p.strip() for p in line.split(";")]
            if len(parts) < 5:
                continue
            name, pub_count, year, affil, topic = (
                parts[0], parts[1], parts[2], parts[3], parts[4]
            )
            # skip header and empty rows
            if not name or not name[0].isalpha() or name.lower() == "author":
                continue
            try:
                count = int(pub_count)
                yr    = int(year) if year else 0
            except ValueError:
                continue
            rows.append({
                "author":       name,
                "count":        count,
                "year":         yr,
                "affiliation":  affil,
                "topic":        topic,
            })
    return rows

def aggregate(rows: list[dict]) -> list[dict]:
    profiles = defaultdict(lambda: {
        "publication_count": 0,
        "latest_year":       0,
        "main_affiliation":  "",
        "topics":            set(),
    })

    for row in rows:
        name = row["author"]
        p = profiles[name]
        p["publication_count"] += row["count"]
        p["topics"].add(row["topic"])

        # keep affiliation from the most recent publication
        if row["year"] > p["latest_year"]:
            p["latest_year"]      = row["year"]
            p["main_affiliation"] = row["affiliation"]

    # convert to list of dicts, sorted by publication_count desc
    result = []
    for name, data in profiles.items():
        result.append({
            "author":            name,
            "publication_count": data["publication_count"],
            "latest_year":       data["latest_year"],
            "main_affiliation":  data["main_affiliation"],
            "topics":            ", ".join(sorted(data["topics"])),
            # profile text used for RAG embeddings
            "profile_text":      build_profile_text(name, data),
        })

    return sorted(result, key=lambda x: x["publication_count"], reverse=True)

def build_profile_text(name: str, data: dict) -> str:
    """
    Human-readable profile text that will be embedded into the vector store.
    The richer the text, the better the semantic search results.
    """
    topics = ", ".join(sorted(data["topics"]))
    affil  = data["main_affiliation"] or "unknown affiliation"
    year   = data["latest_year"] or "unknown year"
    count  = data["publication_count"]

    return (
        f"{name} is a researcher affiliated with {affil}. "
        f"They have {count} publication(s) in this database, "
        f"with the most recent work from {year}. "
        f"Their research topics include: {topics}."
    )

def save(profiles: list[dict], path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "author", "publication_count", "latest_year",
        "main_affiliation", "topics", "profile_text"
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(profiles)

def main():
    print("Loading raw data...")
    rows = load_raw(INPUT)
    print(f"  Loaded {len(rows)} publication records")

    print("Aggregating into reviewer profiles...")
    profiles = aggregate(rows)
    print(f"  Created {len(profiles)} reviewer profiles")

    # stats
    multi_topic = [p for p in profiles if "," in p["topics"]]
    multi_pub   = [p for p in profiles if p["publication_count"] > 1]
    topics_set  = set(t.strip() for p in profiles for t in p["topics"].split(","))
    print(f"  Reviewers with 2+ publications : {len(multi_pub)}")
    print(f"  Reviewers with 2+ topics       : {len(multi_topic)}")
    print(f"  Unique topics                  : {len(topics_set)} → {sorted(topics_set)}")

    print(f"\nTop 5 reviewers by publication count:")
    for p in profiles[:5]:
        print(f"  {p['author']} | {p['publication_count']} pubs | {p['topics']} | {p['main_affiliation']}")

    print(f"\nSample profile_text:")
    print(f"  {profiles[0]['profile_text']}")

    save(profiles, OUTPUT)
    print(f"\nSaved to: {OUTPUT}")

if __name__ == "__main__":
    main()
