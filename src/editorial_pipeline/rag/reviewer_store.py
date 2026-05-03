import csv
import logging
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

log = logging.getLogger(__name__)

COLLECTION_NAME = "reviewers"

class ReviewerStore:
    """
    Manages the Chroma vector store for reviewer profiles.
    - First run: loads CSV, embeds profile_text, persists to disk
    - Subsequent runs: loads from disk directly (fast)
    """

    def __init__(self, profiles_path: str, chroma_dir: str):
        self.profiles_path = profiles_path
        self.chroma_dir    = chroma_dir

        # embedding function — sentence-transformers, działa lokalnie, bez API key
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.client = chromadb.PersistentClient(path=chroma_dir)
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        existing = [c.name for c in self.client.list_collections()]

        if COLLECTION_NAME in existing:
            log.info("Loading existing reviewer collection from Chroma...")
            return self.client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=self.ef,
            )

        log.info("Building reviewer collection for the first time...")
        collection = self.client.create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"},  # cosine similarity dla tekstów
        )
        self._populate(collection)
        return collection

    def _populate(self, collection) -> None:
        profiles = self._load_csv()
        if not profiles:
            log.warning(f"No profiles found in {self.profiles_path}")
            return

        documents = [p["profile_text"] for p in profiles]
        metadatas = [
            {
                "author":            p["author"],
                "publication_count": int(p["publication_count"]),
                "latest_year":       int(p["latest_year"]) if p["latest_year"] else 0,
                "main_affiliation":  p["main_affiliation"],
                "topics":            p["topics"],
            }
            for p in profiles
        ]
        ids = [f"reviewer_{i}" for i in range(len(profiles))]

        # Chroma ma limit 5461 dokumentów na jeden add() — splitujemy na chunki
        chunk_size = 500
        for i in range(0, len(documents), chunk_size):
            collection.add(
                documents=documents[i:i+chunk_size],
                metadatas=metadatas[i:i+chunk_size],
                ids=ids[i:i+chunk_size],
            )
            log.info(f"  Indexed {min(i+chunk_size, len(documents))}/{len(documents)} profiles")

        log.info(f"Collection built with {len(documents)} reviewer profiles")

    def _load_csv(self) -> list[dict]:
        path = Path(self.profiles_path)
        if not path.exists():
            raise FileNotFoundError(f"Reviewer profiles not found: {path}")

        profiles = []
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                if row.get("author") and row.get("profile_text"):
                    profiles.append(row)
        return profiles

    def search(self, query: str, top_n: int = 5) -> list[dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_n,
            include=["metadatas", "distances"],
        )

        reviewers = []
        for meta, distance in zip(
            results["metadatas"][0],
            results["distances"][0],
        ):
            reviewers.append({
                "author":            meta["author"],
                "topics":            meta["topics"],
                "main_affiliation":  meta["main_affiliation"],
                "publication_count": meta["publication_count"],
                "latest_year":       meta["latest_year"],
                "score":             round(1 - distance, 4),  # cosine distance → similarity
            })

        return reviewers

    def reset(self) -> None:
        """Delete and rebuild the collection — useful when CSV changes."""
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self._get_or_create_collection()