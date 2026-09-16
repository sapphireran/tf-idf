#!/usr/bin/env python3
"""TF / DF / IDF / TF-IDF scorer for the tiny personal example.

Mirrors the formulas in this repo's 2012 Perl scripts:

    tf(t, d)  = count(t, d) / tokens(d)
    idf(t)    = ln(N / df(t))
    tfidf(t,d)= tf(t, d) * idf(t)

Differences from tf-idf-values.pl, kept on purpose:

- N is the number of scored documents, not Perl's $#files.
- Only regular files in --corpus are read (no .DS_Store unless you pass it).
- Names that start with '.' are skipped, matching the Perl filter.

Run from the repository root:

    python3 examples/tiny-corpus/compute_tfidf.py --verify
"""

from __future__ import annotations

import argparse
import math
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

# Collapse runs of space / tab / formfeed / vertical tab, like Perl \h\v.
_WS_RE = re.compile(r"[ \t\f\v]+")
_NON_ALNUM_RE = re.compile(r"[^a-zA-Z0-9\s]")


def tokenize_line(line: str) -> tuple[list[str], int]:
    """Return (kept_tokens, word_count_including_empty_splits)."""
    txt = line.rstrip("\n\r")
    txt = _WS_RE.sub(" ", txt)
    txt = txt.lower()
    txt = _NON_ALNUM_RE.sub("", txt)
    pieces = re.split(r" +", txt) if txt else [""]
    kept: list[str] = []
    word_count = 0
    for piece in pieces:
        word_count += 1
        if piece != "":
            kept.append(piece)
    # A completely empty line: Perl split(/ +/, "") yields an empty list, so
    # word_count should not increase. Match that.
    if txt == "":
        return [], 0
    return kept, word_count


def tokenize_document(text: str) -> tuple[list[str], int]:
    kept: list[str] = []
    word_count = 0
    for line in text.splitlines():
        tokens, wc = tokenize_line(line)
        kept.extend(tokens)
        word_count += wc
    return kept, word_count


def iter_corpus_files(corpus: Path) -> list[Path]:
    files = []
    for path in sorted(corpus.iterdir()):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        files.append(path)
    return files


def compute(corpus: Path) -> dict:
    files = iter_corpus_files(corpus)
    if not files:
        raise SystemExit(f"no documents in {corpus}")

    per_doc = {}
    df_files: dict[str, set[str]] = defaultdict(set)

    for path in files:
        text = path.read_text(encoding="utf-8")
        tokens, word_count = tokenize_document(text)
        counts = Counter(tokens)
        if word_count <= 0:
            raise SystemExit(f"{path} produced word_count=0")
        tf = {term: counts[term] / word_count for term in counts}
        per_doc[path.name] = {
            "path": path,
            "tokens": tokens,
            "word_count": word_count,
            "counts": counts,
            "tf": tf,
        }
        for term in counts:
            df_files[term].add(path.name)

    n = len(files)
    idf = {term: math.log(n / len(docset)) for term, docset in df_files.items()}
    for name, info in per_doc.items():
        info["tfidf"] = {term: info["tf"][term] * idf[term] for term in info["tf"]}

    return {
        "n": n,
        "files": files,
        "per_doc": per_doc,
        "df_files": df_files,
        "idf": idf,
    }


def write_tsv(path: Path, rows: list[tuple[str, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(row) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_output(result: dict, output: Path) -> None:
    tf_dir = output / "tf"
    tfidf_dir = output / "tfidf"
    tf_dir.mkdir(parents=True, exist_ok=True)
    tfidf_dir.mkdir(parents=True, exist_ok=True)

    df_rows = [("word", "#docs it exists in", "doc names")]
    for term in sorted(result["df_files"]):
        names = ", ".join(sorted(result["df_files"][term])) + ", "
        df_rows.append((term, str(len(result["df_files"][term])), names))
    write_tsv(output / "df.txt", df_rows)

    idf_rows = [(term, format_float(result["idf"][term])) for term in sorted(result["idf"])]
    write_tsv(output / "idf.txt", idf_rows)

    for filename, info in result["per_doc"].items():
        write_tsv(
            tf_dir / filename,
            [(term, format_float(info["tf"][term])) for term in sorted(info["tf"])],
        )
        write_tsv(
            tfidf_dir / filename,
            [(term, format_float(info["tfidf"][term])) for term in sorted(info["tfidf"])],
        )


def format_float(value: float) -> str:
    # Enough digits to match the hand-calculation anchors without pretending
    # we reproduced Perl's exact stringifier.
    return format(value, ".12g")


def print_rankings(result: dict, k: int = 8) -> None:
    for filename in sorted(result["per_doc"]):
        info = result["per_doc"][filename]
        ranked = sorted(info["tfidf"].items(), key=lambda kv: (-kv[1], kv[0]))
        print(f"## {filename}  (tokens={info['word_count']}, N={result['n']})")
        for term, score in ranked[:k]:
            print(f"  {term:12} {score:.8f}")
        print()


def almost(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def verify(result: dict) -> int:
    errors: list[str] = []

    expected_len = {
        "apple-orchard.txt": 20,
        "ocean-voyage.txt": 18,
        "city-market.txt": 21,
        "night-garden.txt": 19,
    }
    for name, n_tokens in expected_len.items():
        got = result["per_doc"][name]["word_count"]
        if got != n_tokens:
            errors.append(f"{name} word_count {got}, expected {n_tokens}")

    idf = result["idf"]
    checks = {
        "the": 0.0,
        "apple": math.log(2),
        "blossom": math.log(2),
        "in": math.log(4 / 3),
        "orchard": math.log(4),
        "whale": math.log(4),
        "a": math.log(4),
    }
    for term, expected in checks.items():
        got = idf[term]
        if not almost(got, expected):
            errors.append(f"idf({term})={got}, expected {expected}")

    orchard = result["per_doc"]["apple-orchard.txt"]
    if not almost(orchard["tf"]["orchard"], 0.1):
        errors.append("tf(orchard) should be 0.1")
    if not almost(orchard["tf"]["apple"], 0.1):
        errors.append("tf(apple) should be 0.1")
    if not almost(orchard["tfidf"]["orchard"], 0.1 * math.log(4)):
        errors.append("tfidf(orchard) should be 0.1 * ln(4)")
    if not almost(orchard["tfidf"]["apple"], 0.1 * math.log(2)):
        errors.append("tfidf(apple) should be 0.1 * ln(2)")
    if not almost(orchard["tfidf"]["the"], 0.0):
        errors.append("tfidf(the) in orchard should be 0")

    voyage = result["per_doc"]["ocean-voyage.txt"]
    top_voyage = {
        t for t, s in voyage["tfidf"].items() if almost(s, voyage["tfidf"]["whale"])
    }
    if top_voyage != {"ship", "whale"}:
        errors.append(f"voyage top band {sorted(top_voyage)}, expected ship+whale")

    garden = result["per_doc"]["night-garden.txt"]
    top_garden = {
        t
        for t, s in garden["tfidf"].items()
        if almost(s, garden["tfidf"]["garden"])
    }
    if top_garden != {"garden", "moon", "night"}:
        errors.append(f"garden top band {sorted(top_garden)}, expected garden+moon+night")

    market = result["per_doc"]["city-market.txt"]
    if not almost(market["tfidf"]["apple"], market["tf"]["apple"] * math.log(2)):
        errors.append("market apple should use df=2 idf")
    if market["tfidf"]["apple"] >= market["tfidf"]["city"]:
        errors.append("market: apple should rank below exclusive city/market/stall")

    if errors:
        print("VERIFY FAILED", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("VERIFY OK")
    print(f"  N={result['n']}")
    print(f"  vocab={len(result['idf'])}")
    print(f"  idf(the)={idf['the']}")
    print(f"  tfidf(orchard, apple-orchard)={orchard['tfidf']['orchard']:.12f}")
    print(f"  tfidf(apple, apple-orchard)={orchard['tfidf']['apple']:.12f}")
    return 0


def default_tiny_docs() -> Path:
    return Path(__file__).resolve().parent / "docs"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=default_tiny_docs(),
        help="directory of documents (default: this example's docs/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="directory for tf/, df.txt, idf.txt, tfidf/",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="score the tiny corpus and check hand-calculation anchors",
    )
    parser.add_argument(
        "--rank",
        type=int,
        default=8,
        help="how many terms to print per document (0 to skip)",
    )
    args = parser.parse_args(argv)

    corpus = args.corpus
    if args.verify and args.corpus == default_tiny_docs():
        corpus = default_tiny_docs()

    result = compute(corpus)

    if args.output is not None:
        write_output(result, args.output)
        print(f"wrote tables under {args.output}")
    elif not args.verify:
        # Default write location when people run the script as a demo.
        out = Path(__file__).resolve().parent / "output"
        write_output(result, out)
        print(f"wrote tables under {out}")

    if args.rank:
        print_rankings(result, k=args.rank)

    if args.verify:
        if args.output is None:
            # Still produce tables in a temp dir so --verify is side-effect light
            # unless the user asked for an output path. Rankings already printed.
            with tempfile.TemporaryDirectory(prefix="tiny-tfidf-") as tmp:
                write_output(result, Path(tmp))
        return verify(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
