#!/usr/bin/env python3
"""Smoke-check the ranking helpers against the committed output/ snapshot."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = Path(__file__).resolve().parent
sys.path.insert(0, str(EXAMPLES))

from top_terms import load_weights  # noqa: E402


def test_alice_wins_her_own_file() -> None:
    rows = load_weights(ROOT / "output" / "tfidf" / "carroll-alice.txt")
    rows.sort(key=lambda item: (-item[1], item[0]))
    assert rows[0][0] == "alice"
    assert 0.02 < rows[0][1] < 0.03
    the = dict(rows)["the"]
    assert the == 0.0


def test_macbeth_speech_prefix_outranks_the_name() -> None:
    rows = load_weights(ROOT / "output" / "tfidf" / "shakespeare-macbeth.txt")
    weights = dict(rows)
    assert weights["macb"] > weights["macbeth"] > weights["thane"]
    assert weights["haue"] > weights["banquo"]


def test_top_terms_cli() -> None:
    proc = subprocess.run(
        [sys.executable, str(EXAMPLES / "top_terms.py"),
         str(ROOT / "output" / "tfidf" / "austen-emma.txt"), "--n", "3"],
        check=True,
        capture_output=True,
        text=True,
    )
    ranked_rows = []
    for ln in proc.stdout.splitlines():
        parts = ln.split()
        if parts and parts[0].isdigit():
            ranked_rows.append(parts)
    assert ranked_rows[0][1] == "emma"


def test_compare_alice_macbeth_disjoint() -> None:
    proc = subprocess.run(
        [sys.executable, str(EXAMPLES / "compare_documents.py"),
         str(ROOT / "output" / "tfidf" / "carroll-alice.txt"),
         str(ROOT / "output" / "tfidf" / "shakespeare-macbeth.txt"),
         "--n", "10"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "(none)" in proc.stdout
    assert "alice" in proc.stdout
    assert "macb" in proc.stdout


def test_term_report_whale_df() -> None:
    proc = subprocess.run(
        [sys.executable, str(EXAMPLES / "term_report.py"), "whale", "--top", "6"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "df:  6" in proc.stdout
    data_rows = [
        ln for ln in proc.stdout.splitlines()
        if "melville-moby_dick.txt" in ln and "df:" not in ln
    ]
    assert data_rows, proc.stdout
    score = float(data_rows[0].split()[-1])
    assert 0.0049 < score < 0.0050


def test_perl_top_terms() -> None:
    proc = subprocess.run(
        ["perl", str(EXAMPLES / "top_terms.pl"),
         str(ROOT / "output" / "tfidf" / "carroll-alice.txt"), "5"],
        check=True,
        capture_output=True,
        text=True,
    )
    ranked = [ln.split() for ln in proc.stdout.splitlines() if ln.split() and ln.split()[0].isdigit()]
    assert ranked[0][1] == "alice"


def test_austen_pair_beats_alice_macbeth() -> None:
    proc_close = subprocess.run(
        [sys.executable, str(EXAMPLES / "cosine_similarity.py"),
         str(ROOT / "output" / "tfidf" / "austen-emma.txt"),
         str(ROOT / "output" / "tfidf" / "austen-sense.txt")],
        check=True,
        capture_output=True,
        text=True,
    )
    proc_far = subprocess.run(
        [sys.executable, str(EXAMPLES / "cosine_similarity.py"),
         str(ROOT / "output" / "tfidf" / "carroll-alice.txt"),
         str(ROOT / "output" / "tfidf" / "shakespeare-macbeth.txt")],
        check=True,
        capture_output=True,
        text=True,
    )

    def score(stdout: str) -> float:
        for line in stdout.splitlines():
            if "cosine(" in line and "=" in line:
                return float(line.rsplit("=", 1)[1])
        raise AssertionError(stdout)

    assert score(proc_close.stdout) > score(proc_far.stdout)


def main() -> int:
    tests = [
        test_alice_wins_her_own_file,
        test_macbeth_speech_prefix_outranks_the_name,
        test_top_terms_cli,
        test_compare_alice_macbeth_disjoint,
        test_term_report_whale_df,
        test_perl_top_terms,
        test_austen_pair_beats_alice_macbeth,
    ]
    for fn in tests:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"passed {len(tests)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
