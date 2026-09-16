#!/usr/bin/env python3
"""Compute TF-IDF for the tiny example corpus.

This mirrors the personal Gutenberg toy in this repo:

* tokenize by lowercasing, collapsing whitespace, then stripping
  characters outside [a-zA-Z0-9] and spaces
* TF(t, d)  = count(t, d) / number of tokens in d
* IDF(t)    = ln(N / df(t))   with N = number of processed documents
* TF-IDF    = TF * IDF

Natural log matches Perl's log() as used in tf-idf-values.pl.
N is the count of processed documents, which is what the committed
output/idf.txt values imply (N = 18 for the Gutenberg shelf).
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = REPO_ROOT / "examples" / "tiny-corpus"
DEFAULT_OUTPUT = REPO_ROOT / "examples" / "tiny-output"

NON_ALNUM = re.compile(r"[^a-zA-Z0-9\s]")
WHITESPACE = re.compile(r"\s+")


def tokenize(text: str) -> list[str]:
    """Match tf-idf-values.pl: lowercase, squeeze space, drop punctuation."""
    lowered = text.lower()
    squeezed = WHITESPACE.sub(" ", lowered).strip()
    stripped = NON_ALNUM.sub("", squeezed)
    return [tok for tok in stripped.split(" ") if tok]


def iter_documents(corpus_dir: Path) -> list[tuple[str, str]]:
    docs: list[tuple[str, str]] = []
    for path in sorted(corpus_dir.iterdir()):
        if path.name.startswith("."):
            continue
        if not path.is_file():
            continue
        docs.append((path.name, path.read_text(encoding="utf-8")))
    if not docs:
        raise SystemExit(f"no documents found in {corpus_dir}")
    return docs


def compute_tfidf(docs: list[tuple[str, str]]) -> dict:
    tokenized: dict[str, list[str]] = {}
    tf: dict[str, dict[str, float]] = {}
    df: dict[str, set[str]] = defaultdict(set)

    for name, text in docs:
        tokens = tokenize(text)
        tokenized[name] = tokens
        counts = Counter(tokens)
        length = len(tokens)
        tf[name] = {word: count / length for word, count in counts.items()}
        for word in counts:
            df[word].add(name)

    n_docs = len(docs)
    idf = {word: math.log(n_docs / len(doc_set)) for word, doc_set in df.items()}
    tfidf: dict[str, dict[str, float]] = {}
    for name, weights in tf.items():
        tfidf[name] = {word: weights[word] * idf[word] for word in weights}

    return {
        "n_docs": n_docs,
        "tokenized": tokenized,
        "tf": tf,
        "df": {word: sorted(doc_set) for word, doc_set in df.items()},
        "idf": idf,
        "tfidf": tfidf,
    }


def write_outputs(result: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tf_dir = output_dir / "tf"
    tfidf_dir = output_dir / "tfidf"
    tf_dir.mkdir(exist_ok=True)
    tfidf_dir.mkdir(exist_ok=True)

    with (output_dir / "df.txt").open("w", encoding="utf-8") as handle:
        handle.write("word\t#docs it exists in\tdoc names\n")
        for word in sorted(result["df"]):
            names = result["df"][word]
            handle.write(f"{word}\t{len(names)}\t{', '.join(names)}\n")

    with (output_dir / "idf.txt").open("w", encoding="utf-8") as handle:
        for word in sorted(result["idf"]):
            handle.write(f"{word}\t{result['idf'][word]}\n")

    for name, weights in result["tf"].items():
        with (tf_dir / name).open("w", encoding="utf-8") as handle:
            for word in sorted(weights):
                handle.write(f"{word}\t{weights[word]}\n")

    for name, weights in result["tfidf"].items():
        with (tfidf_dir / name).open("w", encoding="utf-8") as handle:
            for word in sorted(weights):
                handle.write(f"{word}\t{weights[word]}\n")


def print_report(result: dict) -> None:
    print(f"documents N = {result['n_docs']}")
    print()
    print("tokens per document")
    for name, tokens in result["tokenized"].items():
        print(f"  {name:20} {len(tokens):3}  {' '.join(tokens)}")
    print()
    print("idf")
    for word in sorted(result["idf"], key=lambda w: (-result["idf"][w], w)):
        df = len(result["df"][word])
        print(f"  {word:12} df={df}  idf={result['idf'][word]:.6f}")
    print()
    print("top tf-idf terms")
    for name in result["tfidf"]:
        ranked = sorted(result["tfidf"][name].items(), key=lambda kv: (-kv[1], kv[0]))
        shown = ", ".join(f"{word}={score:.4f}" for word, score in ranked[:6])
        print(f"  {name:20} {shown}")


# Hand-checked values for the four committed tiny-corpus files.
# Recompute if you edit the corpus texts.
EXPECTED_TOP = {
    "tea-garden.txt": ("tea", 0.1039720770839918),
    "whale-ship.txt": ("whale", 0.23104906018664842),
    "castle-ghost.txt": ("ghost", 0.18082100362433354),
    "market-day.txt": ("bread", 0.18082100362433354),
}


def check_expected(result: dict) -> int:
    """Return 0 if the four-document toy still matches the hand checks."""
    failed = 0
    if result["n_docs"] != 4:
        print(f"check failed: expected N=4, got {result['n_docs']}", file=sys.stderr)
        failed += 1
    for name, (word, score) in EXPECTED_TOP.items():
        got = result["tfidf"].get(name, {}).get(word)
        if got is None:
            print(f"check failed: {name} missing term {word!r}", file=sys.stderr)
            failed += 1
            continue
        if not math.isclose(got, score, rel_tol=1e-12, abs_tol=1e-12):
            print(
                f"check failed: {name} {word} expected {score}, got {got}",
                file=sys.stderr,
            )
            failed += 1
    if failed == 0:
        print("checks passed: top term and score match for all four documents")
    return 1 if failed else 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=DEFAULT_CORPUS,
        help="directory of plain-text documents (default: examples/tiny-corpus)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="directory for df/idf/tf/tfidf tables (default: examples/tiny-output)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed tiny-corpus top terms, then exit",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="print the report without writing tables",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = compute_tfidf(iter_documents(args.corpus))
    print_report(result)
    if not args.no_write and not args.check:
        write_outputs(result, args.output)
        print()
        print(f"wrote tables under {args.output}")
    if args.check:
        return check_expected(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
