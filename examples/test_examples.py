#!/usr/bin/env python3
"""Regression checks for the personal examples (no network, no Gutenberg re-score)."""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_tiny_verify() -> None:
    script = ROOT / "examples" / "tiny-corpus" / "compute_tfidf.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--verify", "--rank", "0"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise AssertionError(proc.stderr or proc.stdout)


def test_ranker_keeps_term_word() -> None:
    rank = load_module("rank_top_terms", ROOT / "examples" / "rank_top_terms.py")
    rows = rank.load_scores(ROOT / "output" / "tfidf" / "austen-emma.txt")
    terms = {term for term, _ in rows}
    if "word" not in terms:
        raise AssertionError("ranker dropped the real term 'word' as a header")
    zeros = sum(1 for _, score in rows if score == 0.0)
    if zeros != 221 or len(rows) != 9312:
        raise AssertionError(f"emma zeros={zeros} vocab={len(rows)}")


def test_idf_junk_suffix() -> None:
    rank = load_module("rank_top_terms", ROOT / "examples" / "rank_top_terms.py")
    assert abs(rank.parse_float("2.89037175789616y") - 2.89037175789616) < 1e-12


def test_committed_tiny_tables() -> None:
    rank = load_module("rank_top_terms", ROOT / "examples" / "rank_top_terms.py")
    orchard = dict(
        rank.load_scores(
            ROOT / "examples" / "tiny-corpus" / "output" / "tfidf" / "apple-orchard.txt"
        )
    )
    if abs(orchard["orchard"] - 0.1 * math.log(4)) > 1e-9:
        raise AssertionError(orchard["orchard"])
    if abs(orchard["apple"] - 0.1 * math.log(2)) > 1e-9:
        raise AssertionError(orchard["apple"])
    if orchard["the"] != 0.0:
        raise AssertionError("the should be zero")


def main() -> int:
    tests = [
        test_tiny_verify,
        test_ranker_keeps_term_word,
        test_idf_junk_suffix,
        test_committed_tiny_tables,
    ]
    failed = 0
    for fn in tests:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 — print and count
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
        else:
            print(f"OK   {fn.__name__}")
    if failed:
        print(f"{failed} failed")
        return 1
    print("all example checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
