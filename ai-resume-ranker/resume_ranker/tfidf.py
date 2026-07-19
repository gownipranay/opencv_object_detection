"""Minimal, dependency-free TF-IDF + cosine similarity implementation.

Kept in pure Python (no numpy/scikit-learn) so the core ranking logic works
even in environments where those packages aren't installed.
"""
import math
import re
from collections import Counter

_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to", "of",
    "for", "with", "as", "by", "is", "are", "was", "were", "be", "been",
    "being", "this", "that", "these", "those", "it", "its", "from", "into",
    "about", "we", "you", "your", "our", "their", "they", "he", "she",
    "will", "would", "can", "could", "should", "have", "has", "had", "not",
    "no", "do", "does", "did", "so", "than", "then", "there", "here",
}

_TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#\.]*")


def tokenize(text: str) -> list:
    """Lowercase, strip punctuation, drop stopwords/short tokens."""
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def build_vocabulary(token_lists):
    vocab = set()
    for tokens in token_lists:
        vocab.update(tokens)
    return sorted(vocab)


def compute_idf(token_lists, vocab):
    n_docs = len(token_lists)
    doc_freq = Counter()
    for tokens in token_lists:
        for term in set(tokens):
            doc_freq[term] += 1
    return {
        term: math.log((1 + n_docs) / (1 + doc_freq[term])) + 1.0
        for term in vocab
    }


def tf_vector(tokens, vocab):
    counts = Counter(tokens)
    total = len(tokens) or 1
    return {term: counts[term] / total for term in vocab if counts[term]}


def tfidf_vector(tokens, vocab, idf):
    tf = tf_vector(tokens, vocab)
    return {term: weight * idf[term] for term, weight in tf.items()}


def cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    if not vec_a or not vec_b:
        return 0.0
    common = set(vec_a) & set(vec_b)
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def tfidf_similarity(text_a: str, text_b: str) -> float:
    """Convenience wrapper: TF-IDF cosine similarity between two raw texts."""
    tokens_a, tokens_b = tokenize(text_a), tokenize(text_b)
    vocab = build_vocabulary([tokens_a, tokens_b])
    idf = compute_idf([tokens_a, tokens_b], vocab)
    vec_a = tfidf_vector(tokens_a, vocab, idf)
    vec_b = tfidf_vector(tokens_b, vocab, idf)
    return cosine_similarity(vec_a, vec_b)
