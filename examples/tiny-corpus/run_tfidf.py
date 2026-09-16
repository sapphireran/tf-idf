#!/usr/bin/env python3
"""Educational TF-IDF runner for the tiny corpus.

This mirrors the two personal Perl scripts in the repository root:

  * tf-idf-values.pl     — per-document TF and corpus DF / IDF
  * tf*idf-product.pl    — TF * IDF for every term in every document

The tokenization rules are the same as the Perl:

  1. collapse runs of whitespace to a single space
  2. lowercase
  3. drop every character that is not a letter, digit, or whitespace
  4. split on one or more spaces
  5. empty tokens still increment the document length (word_count),
     but they are not stored as terms

N, the corpus size used in IDF, is the number of processed documents.
That is the mathematically usual choice. The Perl script instead uses
``$#files`` after ``readdir``, which can count ``.`` / ``..`` / stray
dotfiles. See docs/04-design-notes.md.

Usage:
    python3 examples/tiny-corpus/run_tfidf.py
    python3 examples/tiny-corpus/run_tfidf.py --check
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEXTS = HERE / "texts"
EXPECTED = HERE / "expected"


def tokenize_line(raw: str) -> list[str]:
    """Match the Perl line-normalization in tf-idf-values.pl."""
    txt = raw.rstrip("\n").rstrip("\r")
    txt = re.sub(r"[\t\n\v\f\r ]+", " ", txt)
    txt = txt.lower()
    txt = re.sub(r"[^a-zA-Z0-9\s]", "", txt)
    if txt == "":
        return []
    return re.split(r" +", txt)


def read_document(path: Path) -> tuple[Counter[str], int]:
    tf: Counter[str] = Counter()
    word_count = 0
    for raw in path.read_text(encoding="utf-8").splitlines(keepends=True):
        for token in tokenize_line(raw):
            word_count += 1
            if token != "":
                tf[token] += 1
    return tf, word_count


def corpus_paths() -> list[Path]:
    return sorted(p for p in TEXTS.iterdir() if p.is_file() and not p.name.startswith("."))


def compute(paths: list[Path]) -> dict:
    docs = []
    df: dict[str, set[str]] = defaultdict(set)
    for path in paths:
        tf, word_count = read_document(path)
        docs.append({"name": path.name, "tf_raw": tf, "word_count": word_count})
        for term in tf:
            df[term].add(path.name)

    n = len(docs)
    idf = {term: math.log(n / len(files)) for term, files in df.items()}

    for doc in docs:
        doc["tf"] = {
            term: count / doc["word_count"] if doc["word_count"] else 0.0
            for term, count in doc["tf_raw"].items()
        }
        doc["tfidf"] = {term: doc["tf"][term] * idf[term] for term in doc["tf"]}

    return {"n": n, "df": df, "idf": idf, "docs": docs}


def write_tsv(path: Path, rows: list[tuple[str, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join("\t".join(row) + "\n" for row in rows), encoding="utf-8")


def dump_outputs(result: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "tf").mkdir(exist_ok=True)
    (out_dir / "tfidf").mkdir(exist_ok=True)

    df_rows = [("word", "#docs it exists in", "doc names")]
    idf_rows = []
    for term in sorted(result["df"]):
        names = sorted(result["df"][term])
        df_rows.append((term, str(len(names)), ", ".join(names)))
        idf_rows.append((term, repr(result["idf"][term])))
    write_tsv(out_dir / "df.txt", df_rows)
    write_tsv(out_dir / "idf.txt", idf_rows)

    for doc in result["docs"]:
        tf_rows = [(term, repr(doc["tf"][term])) for term in sorted(doc["tf"])]
        tfidf_rows = [(term, repr(doc["tfidf"][term])) for term in sorted(doc["tfidf"])]
        write_tsv(out_dir / "tf" / doc["name"], tf_rows)
        write_tsv(out_dir / "tfidf" / doc["name"], tfidf_rows)


def ranking_lines(result: dict, k: int = 8) -> list[str]:
    lines = [
        f"corpus size N = {result['n']}",
        f"distinct terms = {len(result['idf'])}",
        "",
    ]
    for doc in result["docs"]:
        ranked = sorted(doc["tfidf"].items(), key=lambda item: (-item[1], item[0]))
        lines.append(f"## {doc['name']}  ({doc['word_count']} tokens)")
        for term, score in ranked[:k]:
            tf = doc["tf"][term]
            df = len(result["df"][term])
            idf = result["idf"][term]
            lines.append(
                f"  {term:14s}  tfidf={score:.6f}  tf={tf:.4f}  "
                f"df={df}  idf={idf:.4f}  count={doc['tf_raw'][term]}"
            )
        lines.append("")
    return lines


def expected_top_terms() -> dict[str, list[str]]:
    """Hand-checked distinctive terms used by --check.

    These are the terms that should outrank generic words in each
    document. The exact floats are recomputed; this only asserts rank.
    """
    return {
        "cats.txt": ["moth", "miso", "cat", "waits"],
        "bread.txt": ["baker", "bread", "dough", "starter"],
        "stars.txt": ["telescope", "saturn", "meteor", "nebula"],
        "garden.txt": ["tomato", "basil", "salad", "vines"],
    }


def check(result: dict) -> int:
    failures = []
    if result["n"] != 4:
        failures.append(f"expected N=4, got {result['n']}")

    # Shared function words should have low or zero IDF.
    for stop in ("the", "a", "and"):
        if stop not in result["idf"]:
            failures.append(f"missing shared term {stop!r}")
            continue
        if result["idf"][stop] > 0.3:
            failures.append(f"{stop!r} idf too high: {result['idf'][stop]}")

    # Distinctive terms should be unique to one document (df=1) except
    # waits/wait which are allowed to be shared.
    for term in ("moth", "miso", "baker", "telescope", "saturn", "tomato", "basil"):
        df = len(result["df"].get(term, ()))
        if df != 1:
            failures.append(f"{term!r} should appear in 1 doc, df={df}")

    expected = expected_top_terms()
    by_name = {doc["name"]: doc for doc in result["docs"]}
    for name, must_appear in expected.items():
        doc = by_name[name]
        ranked = [term for term, _ in sorted(doc["tfidf"].items(), key=lambda item: (-item[1], item[0]))]
        top = ranked[:6]
        for term in must_appear[:2]:
            if term not in top:
                failures.append(f"{name}: expected {term!r} in top 6, got {top}")

    # Worked identity: tfidf == tf * idf for moth in cats.txt
    cats = by_name["cats.txt"]
    moth = cats["tf"]["moth"] * result["idf"]["moth"]
    if abs(moth - cats["tfidf"]["moth"]) > 1e-12:
        failures.append("moth tf*idf identity failed")

    if failures:
        print("CHECK FAILED")
        for item in failures:
            print("  -", item)
        return 1

    print("CHECK PASSED")
    print(f"  N={result['n']}, terms={len(result['idf'])}")
    print("  distinctive terms have df=1")
    print("  shared words the/a/and have low IDF")
    print("  moth identity: "
          f"tf={cats['tf']['moth']:.6f} * "
          f"idf={result['idf']['moth']:.6f} = "
          f"{cats['tfidf']['moth']:.6f}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="run the worked-example assertions instead of printing rankings",
    )
    parser.add_argument(
        "--write-expected",
        action="store_true",
        help="write TSV snapshots under expected/ (same layout as output/)",
    )
    args = parser.parse_args(argv)

    paths = corpus_paths()
    if len(paths) < 2:
        print(f"need at least 2 texts in {TEXTS}", file=sys.stderr)
        return 2

    result = compute(paths)
    print("\n".join(ranking_lines(result)))

    if args.write_expected:
        dump_outputs(result, EXPECTED)
        print(f"wrote snapshots under {EXPECTED}")

    if args.check:
        return check(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
