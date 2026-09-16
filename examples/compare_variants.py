#!/usr/bin/env python3
"""Compare three common weightings on the tiny corpus.

The Gutenberg Perl scripts implement variant A only. This demo shows how
the top term in each short note would move if you used raw TF or a
smoothed IDF instead.

    python3 examples/compare_variants.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tiny_tfidf import DEFAULT_CORPUS, compute_tfidf, iter_documents  # noqa: E402


def smoothed_idf(n_docs: int, df: int) -> float:
    """sklearn-style-ish: ln((N + 1) / (df + 1)) + 1."""
    return math.log((n_docs + 1) / (df + 1)) + 1.0


def top_term(weights: dict[str, float]) -> tuple[str, float]:
    return max(weights.items(), key=lambda item: (item[1], item[0]))


def main() -> int:
    result = compute_tfidf(iter_documents(DEFAULT_CORPUS))
    n_docs = result["n_docs"]
    print(f"N = {n_docs} documents in {DEFAULT_CORPUS}")
    print()
    print(f"{'document':<20} {'raw TF':<18} {'repo TF-IDF':<18} {'smoothed IDF':<18}")
    print("-" * 74)

    for name, tf_weights in result["tf"].items():
        raw_word, raw_score = top_term(tf_weights)
        repo_word, repo_score = top_term(result["tfidf"][name])
        smoothed = {
            word: tf_weights[word] * smoothed_idf(n_docs, len(result["df"][word]))
            for word in tf_weights
        }
        smooth_word, smooth_score = top_term(smoothed)
        print(
            f"{name:<20} "
            f"{raw_word}={raw_score:<10.4f} "
            f"{repo_word}={repo_score:<10.4f} "
            f"{smooth_word}={smooth_score:<10.4f}"
        )

    print()
    print("raw TF ignores rarity, so 'the' wins every note.")
    print("repo TF-IDF is ln(N/df) * TF, matching tf-idf-values.pl.")
    print("smoothed IDF never hits 0; 'the' can still win if its TF is huge.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
