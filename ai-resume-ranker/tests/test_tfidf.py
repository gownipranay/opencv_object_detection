import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from resume_ranker.tfidf import cosine_similarity, tfidf_similarity, tokenize


def test_tokenize_lowercases_and_strips_stopwords():
    tokens = tokenize("The Quick Brown Fox and the Lazy Dog")
    assert "the" not in tokens
    assert "and" not in tokens
    assert "quick" in tokens
    assert "fox" in tokens


def test_identical_texts_have_similarity_one():
    text = "python machine learning engineer with tensorflow experience"
    assert abs(tfidf_similarity(text, text) - 1.0) < 1e-9


def test_unrelated_texts_have_low_similarity():
    a = "python machine learning tensorflow pytorch deep learning"
    b = "grilled cheese sandwich recipe with tomato soup"
    assert tfidf_similarity(a, b) < 0.05


def test_cosine_similarity_handles_empty_vectors():
    assert cosine_similarity({}, {"a": 1.0}) == 0.0
    assert cosine_similarity({"a": 1.0}, {}) == 0.0
