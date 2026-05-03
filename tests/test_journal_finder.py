import pytest
from src.journal_finder.finder import JournalFinder

def test_journal_finder_returns_list():
    finder = JournalFinder()
    results = finder.find(abstract="This paper studies machine learning.")
    assert isinstance(results, list)
