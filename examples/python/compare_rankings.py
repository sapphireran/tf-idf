#!/usr/bin/env python3
"""Compare a freshly scored ranking to a committed tf*idf table.

Useful when checking that tfidf_toy.py still tells the same story as
output/tfidf/ even though the floats are not byte-identical.

    python3 examples/python/compare_rankings.py \\
        --corpus gutenberg \\
        --committed-dir output/tfidf \\
        --top 10
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from tfidf_toy import load_weight_table, ranked_terms, score_corpus


def overlap_at_k(fresh: list[str], committed: list[str]) -> float:
    if not committed:
        return 0.0
    return len(set(fresh) & set(committed)) / len(committed)


def compare_book(fresh_weights: dict[str, float], committed_path: Path, top: int) -> dict:
    committed_weights = load_weight_table(committed_path)
    fresh_rank = [token for token, _ in ranked_terms(fresh_weights, top=top)]
    committed_rank = [token for token, _ in ranked_terms(committed_weights, top=top)]
    return {
        "name": committed_path.name,
        "fresh": fresh_rank,
        "committed": committed_rank,
        "same_top": fresh_rank[:1] == committed_rank[:1],
        "overlap": overlap_at_k(fresh_rank, committed_rank),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare toy rankings to committed tables.")
    parser.add_argument("--corpus", type=Path, default=Path("gutenberg"))
    parser.add_argument("--committed-dir", type=Path, default=Path("output/tfidf"))
    parser.add_argument("--top", type=int, default=10)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    scores = score_corpus(args.corpus)
    by_name = scores.by_name()
    rows = []
    missing = []
    for name, doc in sorted(by_name.items()):
        committed = args.committed_dir / name
        if not committed.is_file():
            missing.append(name)
            continue
        rows.append(compare_book(doc.tfidf, committed, args.top))

    print(f"# top-{args.top} overlap  (fresh N={scores.n_documents})")
    print(f"{'book':<28s} {'top?':<6s} {'overlap':>8s}  fresh-1st          committed-1st")
    for row in rows:
        flag = "yes" if row["same_top"] else "NO"
        print(
            f"{row['name']:<28s} {flag:<6s} {row['overlap']:8.2f}  "
            f"{row['fresh'][0]:<16s}  {row['committed'][0]}"
        )
        if row["overlap"] < 1:
            only_fresh = [t for t in row["fresh"] if t not in row["committed"]]
            only_committed = [t for t in row["committed"] if t not in row["fresh"]]
            if only_fresh or only_committed:
                print(f"    only fresh: {only_fresh}  only committed: {only_committed}")

    if missing:
        print(f"\nno committed table for: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
