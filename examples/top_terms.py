#!/usr/bin/env python3
"""Print the highest tf-idf (or tf) terms from a directory of TSV files.

Each file is treated as one document. Lines are `term<TAB>score`, the same
layout as output/tfidf and examples/tiny-corpus/output/tfidf.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def read_scores(path: Path) -> list[tuple[float, str]]:
    rows: list[tuple[float, str]] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        parts = raw.split("\t")
        if len(parts) < 2:
            raise SystemExit(f"{path}:{line_no}: expected term<TAB>score")
        try:
            score = float(parts[1])
        except ValueError as exc:
            raise SystemExit(f"{path}:{line_no}: not a float: {parts[1]!r}") from exc
        rows.append((score, parts[0]))
    rows.sort(key=lambda item: (-item[0], item[1]))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("output/tfidf"),
        help="directory of term<TAB>score files (default: output/tfidf)",
    )
    parser.add_argument("--n", type=int, default=15, help="terms per file")
    parser.add_argument(
        "--files",
        nargs="*",
        help="optional basenames to include (default: every .txt file)",
    )
    args = parser.parse_args(argv)

    if not args.path.is_dir():
        raise SystemExit(f"not a directory: {args.path}")

    files = sorted(
        p
        for p in args.path.iterdir()
        if p.is_file() and p.suffix == ".txt" and not p.name.startswith(".")
    )
    if args.files:
        wanted = set(args.files)
        files = [p for p in files if p.name in wanted]
        missing = wanted - {p.name for p in files}
        if missing:
            raise SystemExit(f"not found under {args.path}: {', '.join(sorted(missing))}")

    if not files:
        raise SystemExit(f"no files in {args.path}")

    for path in files:
        print(f"== {path.name}")
        for score, term in read_scores(path)[: args.n]:
            print(f"{term:20} {score:.8f}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
