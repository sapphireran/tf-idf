#!/usr/bin/env python3
"""Regression checks for the personal examples.

    python3 examples/run_checks.py
"""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXAMPLES = REPO / "examples"


def run(args: list[str]) -> str:
    completed = subprocess.run(
        args,
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def assert_in(needle: str, haystack: str, label: str) -> None:
    if needle not in haystack:
        raise AssertionError(f"{label}: expected {needle!r} in output\n{haystack}")


def main() -> int:
    tiny = run([sys.executable, str(EXAMPLES / "tiny_tfidf.py"), "--check"])
    assert_in("checks passed", tiny, "tiny_tfidf --check")

    alice = run(
        [sys.executable, str(EXAMPLES / "rank_terms.py"), "carroll-alice", "--top", "3"]
    )
    assert_in("alice", alice.splitlines()[1], "rank alice")

    whale_q = run(
        [sys.executable, str(EXAMPLES / "query_documents.py"), "whale", "ahab", "pequod"]
    )
    assert_in("melville-moby_dick.txt", whale_q.splitlines()[2], "query whale")

    stop = run([sys.executable, str(EXAMPLES / "query_documents.py"), "the", "and", "of"])
    first_score = float(stop.splitlines()[2].split()[1])
    if not math.isclose(first_score, 0.0, abs_tol=1e-12):
        raise AssertionError(f"stopword query should be 0, got {first_score}")

    tea = run(
        [
            sys.executable,
            str(EXAMPLES / "query_documents.py"),
            "--dir",
            str(EXAMPLES / "tiny-output" / "tfidf"),
            "tea",
            "rabbit",
        ]
    )
    assert_in("tea-garden.txt", tea.splitlines()[2], "tiny tea query")

    explained = run([sys.executable, str(EXAMPLES / "explain_term.py"), "alice"])
    assert_in("df   : 3", explained, "explain alice df")
    assert_in("carroll-alice.txt", explained, "explain alice docs")

    variants = run([sys.executable, str(EXAMPLES / "compare_variants.py")])
    assert_in("whale=", variants, "compare variants")

    tokens = run(
        [sys.executable, str(EXAMPLES / "inspect_tokenize.py"), "Alice's Adventures"]
    )
    assert_in("alices", tokens, "tokenizer possessive")

    print("all example checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
