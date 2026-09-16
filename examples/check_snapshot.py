#!/usr/bin/env python3
"""Sanity-check the frozen Gutenberg output/ tables.

Confirms, for a handful of documented terms:

* idf(t) == ln(18 / df(t))
* tfidf(t, d) == tf(t, d) * idf(t)
* collection-wide words have IDF 0
* Alice / Melville / Emma winners match the worked-examples write-up

This does not rerun the Perl. It only reads output/.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "output"
N_DOCS = 18


def load_scores(path: Path) -> dict[str, float]:
    scores: dict[str, float] = {}
    with path.open(encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            if not line or line.startswith("word"):
                continue
            term, sep, rest = line.partition("\t")
            if not sep:
                continue
            value_str = rest.split("\t", 1)[0].strip()
            try:
                scores[term] = float(value_str)
            except ValueError:
                continue
    return scores


def load_df_counts(path: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    with path.open(encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            if not line or line.startswith("word"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            try:
                counts[parts[0]] = int(parts[1])
            except ValueError:
                continue
    return counts


def almost(left: float, right: float, rel: float = 1e-9) -> None:
    scale = max(1.0, abs(left), abs(right))
    if abs(left - right) > rel * scale:
        raise AssertionError(f"{left!r} != {right!r}")


def check_idf(idf: dict[str, float], df: dict[str, int], term: str) -> None:
    if term not in idf or term not in df:
        raise AssertionError(f"missing {term} in idf/df")
    almost(idf[term], math.log(N_DOCS / df[term]))


def check_product(term: str, doc: str, tf: dict[str, float], idf: dict[str, float], tfidf: dict[str, float]) -> None:
    almost(tfidf[term], tf[term] * idf[term])


def top_term(tfidf: dict[str, float]) -> str:
    return max(tfidf.items(), key=lambda item: (item[1], item[0]))[0]


def main() -> int:
    idf = load_scores(OUTPUT / "idf.txt")
    df = load_df_counts(OUTPUT / "df.txt")

    try:
        if not idf or not df:
            raise AssertionError("empty idf or df table")

        unique = [term for term, value in idf.items() if abs(value - math.log(N_DOCS)) < 1e-9]
        if not unique:
            raise AssertionError("no term has ln(18) IDF; snapshot N is not 18")

        for term in ("alice", "whale", "ahab", "emma", "the", "and", "a", "gryphon"):
            check_idf(idf, df, term)

        if df["the"] != N_DOCS or idf["the"] != 0.0:
            raise AssertionError("the should appear in all 18 books with IDF 0")
        if df["alice"] != 3:
            raise AssertionError(f"alice df expected 3, got {df['alice']}")
        if df["whale"] != 6:
            raise AssertionError(f"whale df expected 6, got {df['whale']}")
        if df["ahab"] != 2:
            raise AssertionError(f"ahab df expected 2, got {df['ahab']}")

        alice_tf = load_scores(OUTPUT / "tf" / "carroll-alice.txt")
        alice_tfidf = load_scores(OUTPUT / "tfidf" / "carroll-alice.txt")
        check_product("alice", "carroll-alice", alice_tf, idf, alice_tfidf)
        almost(alice_tfidf["alice"], 0.025956780390307)
        if top_term(alice_tfidf) != "alice":
            raise AssertionError(f"Alice top term is {top_term(alice_tfidf)!r}, not 'alice'")

        moby_tf = load_scores(OUTPUT / "tf" / "melville-moby_dick.txt")
        moby_tfidf = load_scores(OUTPUT / "tfidf" / "melville-moby_dick.txt")
        check_product("whale", "melville-moby_dick", moby_tf, idf, moby_tfidf)
        check_product("ahab", "melville-moby_dick", moby_tf, idf, moby_tfidf)
        if top_term(moby_tfidf) != "whale":
            raise AssertionError(f"Moby-Dick top term is {top_term(moby_tfidf)!r}, not 'whale'")

        emma_tfidf = load_scores(OUTPUT / "tfidf" / "austen-emma.txt")
        if top_term(emma_tfidf) != "emma":
            raise AssertionError(f"Emma top term is {top_term(emma_tfidf)!r}, not 'emma'")

        hamlet_tfidf = load_scores(OUTPUT / "tfidf" / "shakespeare-hamlet.txt")
        if top_term(hamlet_tfidf) != "ham":
            raise AssertionError(
                f"Hamlet top term is {top_term(hamlet_tfidf)!r}, expected speech prefix 'ham'"
            )
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        return 1
    except OSError as exc:
        print(f"FAIL: {exc}")
        return 1

    print("Gutenberg snapshot checks passed (N=18, worked-example identities hold)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
