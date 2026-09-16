#!/usr/bin/env python3
"""Rank terms from already-written tf-idf tables (the committed output/)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple


def read_tfidf_table(path: Path) -> List[Tuple[str, float]]:
    rows: List[Tuple[str, float]] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw.strip():
            continue
        term, _, value = raw.partition("\t")
        if not value:
            continue
        try:
            score = float(value)
        except ValueError:
            continue
        rows.append((term, score))
    rows.sort(key=lambda item: (-item[1], item[0]))
    return rows


def format_section(name: str, rows: Sequence[Tuple[str, float]], top: int, drop_zero: bool) -> str:
    chosen = []
    for term, score in rows:
        if drop_zero and score == 0.0:
            continue
        chosen.append((term, score))
        if len(chosen) >= top:
            break
    lines = [f"## {name}", ""]
    lines.append("| rank | term | tf-idf |")
    lines.append("| ---: | --- | ---: |")
    for rank, (term, score) in enumerate(chosen, start=1):
        lines.append(f"| {rank} | `{term}` | {score:.8g} |")
    lines.append("")
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print the highest tf-idf terms from output/tfidf (or any matching directory)."
    )
    parser.add_argument(
        "--from-output",
        type=Path,
        default=Path("output/tfidf"),
        help="Directory of term<TAB>score files.",
    )
    parser.add_argument("--file", help="Single filename inside that directory.")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument(
        "--keep-zeros",
        action="store_true",
        help="Keep terms whose score is 0 (universal words with idf=0).",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        help="Write a markdown report instead of printing.",
    )
    return parser


def iter_tables(directory: Path, only: Optional[str]) -> List[Path]:
    if not directory.is_dir():
        raise FileNotFoundError(f"tf-idf directory not found: {directory}")
    if only:
        path = directory / only
        if not path.is_file():
            raise FileNotFoundError(path)
        return [path]
    paths = [
        entry
        for entry in sorted(directory.iterdir())
        if entry.is_file() and not entry.name.startswith(".")
    ]
    if not paths:
        raise ValueError(f"no tables in {directory}")
    return paths


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    paths = iter_tables(args.from_output, args.file)
    chunks = [
        "# Gutenberg tf-idf top terms",
        "",
        "Ranked from the committed `output/tfidf/` tables. Zeros (terms with "
        "`idf = 0`) are omitted unless `--keep-zeros` was passed.",
        "",
    ]
    drop_zero = not args.keep_zeros
    for path in paths:
        chunks.append(format_section(path.name, read_tfidf_table(path), args.top, drop_zero))
    text = "\n".join(chunks).rstrip() + "\n"
    if args.markdown:
        args.markdown.write_text(text, encoding="utf-8")
        print(f"wrote {args.markdown}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
