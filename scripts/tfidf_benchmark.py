#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Personal TF-IDF benchmark for this Gutenberg toy corpus.

This file is a from-scratch personal study script. It does not import,
copy, or wrap any company library. The only inputs it needs are the
public-domain texts under ``gutenberg/`` and, optionally, the
already-checked-in ``output/`` tables from the 2012 Perl scripts.

Why this exists
---------------
The original Perl pair (``tf-idf-values.pl`` then ``tf*idf-product.pl``)
writes TF, DF, IDF, and TF-IDF tables but does not time anything and
does not explain the arithmetic. I wanted a single script I can run
from the repo root that:

1. Reimplements the same tokenizer and the same classic TF-IDF formula.
2. Prints wall-clock time for each stage so I can see where a naive
   in-memory pass spends its time on this 18-book sample.
3. Cross-checks the numbers against ``output/idf.txt`` and the
   per-document TF / TF-IDF files.
4. Shows the highest-weighted terms per book, which is the whole
   point of computing TF-IDF in the first place.

The formulas, written once so the code below has a north star::

    tf(term, doc)  = count(term, doc) / word_count(doc)
    idf(term)      = ln(N / df(term))          # --variant classic
    tfidf          = tf * idf

``word_count`` follows the Perl quirk: every field from ``split(/ +/)``
is counted, including a leading empty field on lines that began with
whitespace. See ``docs/algorithm.md``.

How to run
----------
From the repository root::

    python3 scripts/tfidf_benchmark.py
    python3 scripts/tfidf_benchmark.py --self-test
    python3 scripts/tfidf_benchmark.py --repeats 5 --top 8

``--self-test`` does not read ``gutenberg/``. It recomputes the
three-document postcard in ``docs/algorithm.md`` and exits non-zero
if any cell drifts.

This is personal-only code. Keep company sources out of this tree.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------
# The 2012 Perl does, per line:
#   chomp
#   s/[\h\v]+/ /g
#   tr/[A-Z]/[a-z]/
#   s/[^a-zA-Z\d\s]//g
#   split(/ +/, $txt)
#
# Perl's \h and \v together are "any whitespace" on this ASCII corpus.
# Python has no \h / \v in the same sense, so the character class below
# lists the ASCII controls that Gutenberg actually uses. Expanding it to
# full Unicode whitespace would change counts on a different collection;
# it would not change counts here.
#
# Perl split(/ +/) discards trailing empty fields and treats a string
# that is only separators as an empty list. re.split does not, so
# perl_split_spaces() patches that. Leading empties are kept, which is
# what inflates word_count on indented lines.

_WHITESPACE_RUN = re.compile(r"[\t\n\x0b\x0c\r ]+")
_NOT_ALNUM_OR_SPACE = re.compile(r"[^a-zA-Z0-9\s]")
_SPACES = re.compile(r" +")


def perl_split_spaces(text: str) -> list[str]:
    """Split on one or more spaces the way Perl ``split(/ +/, $txt)`` does.

    Trailing empty fields are dropped. A whitespace-only string becomes
    ``[]``, not ``['']``. A leading empty field is preserved so
    ``' hello'`` yields ``['', 'hello']``.
    """
    parts = _SPACES.split(text)
    while parts and parts[-1] == "":
        parts.pop()
    if parts == [""]:
        return []
    return parts


def tokenize_line(line: str) -> list[str]:
    """Apply the 2012 per-line cleanup. ``line`` should already be chomped."""
    # Collapse horizontal + vertical whitespace to a single space before
    # stripping punctuation. That matches the Perl order: a hyphen
    # surrounded by spaces becomes two spaces and then a clean split,
    # while ``mock-turtle`` loses the hyphen and becomes one token.
    text = _WHITESPACE_RUN.sub(" ", line)
    text = text.lower()
    text = _NOT_ALNUM_OR_SPACE.sub("", text)
    return perl_split_spaces(text)


def chomp(line: str) -> str:
    """Perl ``chomp``: remove a single trailing input-record separator."""
    if line.endswith("\n"):
        return line[:-1]
    return line


# ---------------------------------------------------------------------------
# IDF variants
# ---------------------------------------------------------------------------
# Only "classic" is allowed to be compared against output/idf.txt.
# The others are here so I can answer "what would sklearn have done"
# without opening another project.


def idf_classic(n_docs: int, df: int) -> float:
    """Sparck-Jones / 2012 form: ``ln(N / df)``."""
    return math.log(n_docs / df)


def idf_smooth(n_docs: int, df: int) -> float:
    """Add-one on the denominator only: ``ln(N / (1 + df))``.

    Terms that appear in every document go slightly negative, because
    ``N / (N + 1) < 1``. Classic IDF is exactly zero in that case.
    """
    return math.log(n_docs / (1.0 + df))


def idf_sklearnish(n_docs: int, df: int) -> float:
    """sklearn-style smoothed IDF with a leading one.

    ``ln((N + 1) / (df + 1)) + 1``. Never zero, never negative. Useful
    as a contrast, useless for matching ``output/``.
    """
    return math.log((n_docs + 1.0) / (df + 1.0)) + 1.0


IDF_VARIANTS = {
    "classic": idf_classic,
    "smooth": idf_smooth,
    "sklearnish": idf_sklearnish,
}


# ---------------------------------------------------------------------------
# In-memory collection
# ---------------------------------------------------------------------------


@dataclass
class Document:
    """One Gutenberg file after a single tokenize pass."""

    name: str
    raw_bytes: int
    # Perl $word_count: every split field, empty or not.
    word_count: int
    # Fields that actually updated %tf.
    kept_tokens: int
    counts: dict[str, int]

    def tf(self, term: str) -> float:
        if self.word_count == 0:
            return 0.0
        return self.counts.get(term, 0) / self.word_count


@dataclass
class Collection:
    documents: list[Document]
    # term -> number of documents it occurs in (binary per file).
    df: dict[str, int]
    # How many directory entries readdir would have seen, including
    # "." and "..". Used only by --n-mode perl-last-index.
    readdir_count: int

    @property
    def n_documents(self) -> int:
        return len(self.documents)

    @property
    def vocab_size(self) -> int:
        return len(self.df)

    def n_for_idf(self, n_mode: str) -> int:
        if n_mode == "documents":
            return self.n_documents
        if n_mode == "perl-last-index":
            # $#files == last index == count - 1.
            return max(self.readdir_count - 1, 1)
        raise ValueError(f"unknown n-mode: {n_mode!r}")


@dataclass
class StageTimes:
    """Seconds for one pass through the pipeline."""

    read_files: float = 0.0
    tokenize_and_count: float = 0.0
    compute_idf: float = 0.0
    compute_tfidf: float = 0.0
    rank_top_terms: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "read_files": self.read_files,
            "tokenize_and_count": self.tokenize_and_count,
            "compute_idf": self.compute_idf,
            "compute_tfidf": self.compute_tfidf,
            "rank_top_terms": self.rank_top_terms,
            "total": self.total,
        }

    @property
    def total(self) -> float:
        return (
            self.read_files
            + self.tokenize_and_count
            + self.compute_idf
            + self.compute_tfidf
            + self.rank_top_terms
        )


@dataclass
class CompareBucket:
    gold_terms: int = 0
    computed_terms: int = 0
    shared_terms: int = 0
    missing_in_computed: int = 0
    extra_in_computed: int = 0
    max_abs_delta: float = 0.0
    mismatches: int = 0

    def ok(self, max_mismatches: int = 0) -> bool:
        return (
            self.missing_in_computed == 0
            and self.extra_in_computed == 0
            and self.mismatches <= max_mismatches
        )


@dataclass
class BenchmarkReport:
    corpus: Path
    n_mode: str
    variant: str
    n_used: int
    repeats: int
    times: list[StageTimes] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    idf: dict[str, float] = field(default_factory=dict)
    tfidf: dict[str, dict[str, float]] = field(default_factory=dict)
    top_terms: dict[str, list[tuple[str, float]]] = field(default_factory=dict)
    df: dict[str, int] = field(default_factory=dict)
    compare: dict[str, CompareBucket] = field(default_factory=dict)

    @property
    def best_times(self) -> StageTimes:
        if not self.times:
            return StageTimes()
        best = min(self.times, key=lambda t: t.total)
        return best

    @property
    def mean_total(self) -> float:
        if not self.times:
            return 0.0
        return statistics.fmean(t.total for t in self.times)


# ---------------------------------------------------------------------------
# I/O and counting
# ---------------------------------------------------------------------------


def list_corpus_names(corpus: Path) -> list[str]:
    """Names the Perl would tokenize: anything that does not start with '.'."""
    names = [name for name in os.listdir(corpus) if not name.startswith(".")]
    # Sort so the report is stable. Perl uses readdir order, which does
    # not change the numeric TF / IDF / TF-IDF cells.
    names.sort()
    return names


def readdir_entry_count(corpus: Path) -> int:
    """Approximate Perl ``readdir`` cardinality, including ``.`` and ``..``."""
    # os.listdir omits those two; Perl's readdir does not.
    return 2 + len(os.listdir(corpus))


def document_from_text(name: str, raw: str, raw_bytes: int) -> Document:
    """Tokenize one file and tally raw term counts.

    Line iteration follows Perl ``@text = <IN>`` plus ``chomp`` (see
    ``iter_chomp_lines``). The TF denominator follows the Perl
    ``$word_count++`` that runs *before* the empty-field skip.
    """
    counts: dict[str, int] = {}
    word_count = 0
    kept = 0
    for line in iter_chomp_lines(raw):
        fields = tokenize_line(line)
        for field in fields:
            word_count += 1
            if field != "":
                counts[field] = counts.get(field, 0) + 1
                kept += 1
    return Document(
        name=name,
        raw_bytes=raw_bytes,
        word_count=word_count,
        kept_tokens=kept,
        counts=counts,
    )


def iter_chomp_lines(raw: str) -> Iterable[str]:
    """Yield chomped lines the way Perl ``@text = <IN>`` plus ``chomp`` does.

    A file that ends with a newline does not produce an extra empty
    line. A file that does not end with a newline still yields its
    last partial line. ``\\r`` is left in place for the whitespace
    collapse step, matching a default ``$/ = "\\n"`` chomp.
    """
    start = 0
    length = len(raw)
    while start < length:
        nl = raw.find("\n", start)
        if nl == -1:
            yield raw[start:]
            return
        yield chomp(raw[start : nl + 1])
        start = nl + 1


def load_collection(corpus: Path) -> tuple[Collection, float, float]:
    """Read every kept file and tally TF / DF. Returns timing halves."""
    names = list_corpus_names(corpus)
    readdir_count = readdir_entry_count(corpus)

    t0 = time.perf_counter()
    blobs: list[tuple[str, str, int]] = []
    for name in names:
        path = corpus / name
        # latin-1 is a lossless bytes-to-chars map, closest to a 2012
        # Perl open() with no encoding layer on this ASCII corpus.
        data = path.read_bytes()
        blobs.append((name, data.decode("latin-1"), len(data)))
    read_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    documents: list[Document] = []
    df_sets: dict[str, set[str]] = {}
    for name, raw, nbytes in blobs:
        doc = document_from_text(name, raw, nbytes)
        documents.append(doc)
        for term in doc.counts:
            bucket = df_sets.get(term)
            if bucket is None:
                df_sets[term] = {name}
            else:
                bucket.add(name)
    df = {term: len(files) for term, files in df_sets.items()}
    tok_s = time.perf_counter() - t1
    return Collection(documents, df, readdir_count), read_s, tok_s


def compute_idf(
    collection: Collection, variant: str, n_mode: str
) -> tuple[dict[str, float], float, int]:
    fn = IDF_VARIANTS[variant]
    n_used = collection.n_for_idf(n_mode)
    t0 = time.perf_counter()
    idf = {term: fn(n_used, df) for term, df in collection.df.items()}
    return idf, time.perf_counter() - t0, n_used


def compute_tfidf(
    collection: Collection, idf: Mapping[str, float]
) -> tuple[dict[str, dict[str, float]], float]:
    t0 = time.perf_counter()
    out: dict[str, dict[str, float]] = {}
    for doc in collection.documents:
        if doc.word_count == 0:
            out[doc.name] = {}
            continue
        scale = 1.0 / doc.word_count
        # Multiply in one pass over this document's own vocab. Terms
        # that never occur here are omitted, matching the Perl tables.
        out[doc.name] = {
            term: count * scale * idf[term] for term, count in doc.counts.items()
        }
    return out, time.perf_counter() - t0


def rank_top_terms(
    tfidf: Mapping[str, Mapping[str, float]], top: int
) -> tuple[dict[str, list[tuple[str, float]]], float]:
    t0 = time.perf_counter()
    ranked: dict[str, list[tuple[str, float]]] = {}
    for name, scores in tfidf.items():
        items = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        ranked[name] = items[:top]
    return ranked, time.perf_counter() - t0


# ---------------------------------------------------------------------------
# Comparison against the checked-in Perl tables
# ---------------------------------------------------------------------------

# Perl's default float printer and Python's IEEE doubles agree to well
# past 1e-12 on this corpus. A mismatch larger than this is a real
# tokenizer or N disagreement, not rounding.
ABS_TOL = 1e-12


def parse_perl_float(value: str) -> float:
    """Parse a Perl-printed float, including one known corrupt gold cell.

    ``output/idf.txt`` line for ``thatyou`` is ``2.89037175789616y`` —
    a trailing letter glued onto an otherwise ordinary ``ln(18)``. I
    strip a run of trailing letters rather than failing the whole
    comparison over that one 2012 typo.
    """
    try:
        return float(value)
    except ValueError:
        cleaned = value.rstrip("abcdefghijklmnopqrstuvwxyz")
        return float(cleaned)


def load_term_float_table(path: Path) -> dict[str, float]:
    table: dict[str, float] = {}
    with path.open("r", encoding="latin-1") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            term, value = line.split("\t", 1)
            table[term] = parse_perl_float(value)
    return table


def compare_tables(
    gold: Mapping[str, float], computed: Mapping[str, float]
) -> CompareBucket:
    gold_keys = set(gold)
    computed_keys = set(computed)
    shared = gold_keys & computed_keys
    bucket = CompareBucket(
        gold_terms=len(gold_keys),
        computed_terms=len(computed_keys),
        shared_terms=len(shared),
        missing_in_computed=len(gold_keys - computed_keys),
        extra_in_computed=len(computed_keys - gold_keys),
    )
    max_delta = 0.0
    mismatches = 0
    for term in shared:
        delta = abs(gold[term] - computed[term])
        if delta > max_delta:
            max_delta = delta
        if delta > ABS_TOL:
            mismatches += 1
    bucket.max_abs_delta = max_delta
    bucket.mismatches = mismatches
    return bucket


def compare_against_output(
    report: BenchmarkReport, output_dir: Path
) -> dict[str, CompareBucket]:
    results: dict[str, CompareBucket] = {}
    idf_path = output_dir / "idf.txt"
    if idf_path.is_file():
        results["idf"] = compare_tables(load_term_float_table(idf_path), report.idf)

    tf_dir = output_dir / "tf"
    if tf_dir.is_dir() and report.documents:
        gold: dict[str, float] = {}
        computed: dict[str, float] = {}
        for doc in report.documents:
            gold_path = tf_dir / doc.name
            if not gold_path.is_file():
                continue
            for term, value in load_term_float_table(gold_path).items():
                gold[f"{doc.name}::{term}"] = value
                computed[f"{doc.name}::{term}"] = doc.tf(term)
        results["tf"] = compare_tables(gold, computed)

    tfidf_dir = output_dir / "tfidf"
    if tfidf_dir.is_dir() and report.tfidf:
        gold = {}
        computed = {}
        for name, scores in report.tfidf.items():
            gold_path = tfidf_dir / name
            if not gold_path.is_file():
                continue
            for term, value in load_term_float_table(gold_path).items():
                gold[f"{name}::{term}"] = value
                computed[f"{name}::{term}"] = scores.get(term, float("nan"))
        results["tfidf"] = compare_tables(gold, computed)

    return results


# ---------------------------------------------------------------------------
# Self-test (the postcard corpus from docs/algorithm.md)
# ---------------------------------------------------------------------------

SELF_TEST_DOCS = {
    "doc_a": "the cat sat\n",
    "doc_b": "the dog sat\n",
    "doc_c": "the cat\n",
}


def expected_self_test() -> tuple[dict[str, float], dict[str, float]]:
    """Hand-computed IDF and two TF-IDF cells from the algorithm note."""
    idf = {
        "the": math.log(3 / 3),
        "cat": math.log(3 / 2),
        "sat": math.log(3 / 2),
        "dog": math.log(3 / 1),
    }
    tfidf_cells = {
        "doc_a::cat": (1 / 3) * math.log(3 / 2),
        "doc_b::dog": (1 / 3) * math.log(3 / 1),
    }
    return idf, tfidf_cells


def run_self_test() -> int:
    documents = [
        document_from_text(name, raw, len(raw.encode("latin-1")))
        for name, raw in SELF_TEST_DOCS.items()
    ]
    df: dict[str, int] = {}
    for doc in documents:
        for term in doc.counts:
            df[term] = df.get(term, 0) + 1
    collection = Collection(documents, df, readdir_count=5)
    idf, _, n_used = compute_idf(collection, "classic", "documents")
    tfidf, _ = compute_tfidf(collection, idf)
    want_idf, want_cells = expected_self_test()

    print("Personal TF-IDF self-test (3 synthetic documents)")
    print(f"  N used: {n_used}")
    print("  documents:")
    for name, raw in SELF_TEST_DOCS.items():
        print(f"    {name}: {raw.strip()!r}")
    print()

    failed = 0
    print("  IDF")
    for term in ("the", "cat", "sat", "dog"):
        got = idf[term]
        want = want_idf[term]
        ok = abs(got - want) <= ABS_TOL
        mark = "ok" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"    {term:5}  got={got:.16f}  want={want:.16f}  {mark}")

    print("  TF-IDF cells")
    got_cells = {
        "doc_a::cat": tfidf["doc_a"]["cat"],
        "doc_b::dog": tfidf["doc_b"]["dog"],
    }
    for key, want in want_cells.items():
        got = got_cells[key]
        ok = abs(got - want) <= ABS_TOL
        mark = "ok" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"    {key:12}  got={got:.16f}  want={want:.16f}  {mark}")

    # the must be exactly zero, not a tiny float leftover.
    if tfidf["doc_a"]["the"] != 0.0 or tfidf["doc_c"]["the"] != 0.0:
        print("  FAIL: idf(the) did not zero out TF-IDF")
        failed += 1
    else:
        print("  the is zero in every document (ok)")

    if failed:
        print(f"\nself-test failed: {failed} check(s)")
        return 1
    print("\nself-test passed")
    return 0


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def fmt_seconds(value: float) -> str:
    if value >= 1.0:
        return f"{value:8.4f}s"
    return f"{value * 1000.0:8.2f}ms"


def fmt_int(value: int) -> str:
    return f"{value:,}"


def collection_stats_lines(report: BenchmarkReport) -> list[str]:
    docs = report.documents
    raw_bytes = sum(d.raw_bytes for d in docs)
    word_count = sum(d.word_count for d in docs)
    kept = sum(d.kept_tokens for d in docs)
    empties = word_count - kept
    vocab = len(report.idf)
    n = report.n_used
    df_n = sum(1 for df in report.df.values() if df == n)
    df_1 = sum(1 for df in report.df.values() if df == 1)
    lines = [
        f"  documents            {fmt_int(len(docs))}",
        f"  N used for IDF       {fmt_int(n)}   ({report.n_mode})",
        f"  raw bytes            {fmt_int(raw_bytes)}",
        f"  split fields         {fmt_int(word_count)}   (Perl word_count)",
        f"  kept tokens          {fmt_int(kept)}",
        f"  empty split fields   {fmt_int(empties)}   (leading-space lines)",
        f"  vocabulary           {fmt_int(vocab)}",
        f"  terms with df = 1    {fmt_int(df_1)}   (max IDF)",
        f"  terms with df = N    {fmt_int(df_n)}   (IDF 0 in classic)",
    ]
    return lines


def format_report(report: BenchmarkReport) -> str:
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append("Personal TF-IDF benchmark")
    lines.append(f"  corpus     {report.corpus}")
    lines.append(f"  variant    {report.variant}")
    lines.append(f"  n-mode     {report.n_mode} (N={report.n_used})")
    lines.append(f"  repeats    {report.repeats}")
    lines.append("=" * 72)
    lines.append("")
    lines.append("Stage timings (best-of-repeats, plus mean total)")
    best = report.best_times
    for name, value in best.as_dict().items():
        label = "TOTAL" if name == "total" else name
        lines.append(f"  {label:20} {fmt_seconds(value)}")
    if report.repeats > 1:
        lines.append(f"  {'mean TOTAL':20} {fmt_seconds(report.mean_total)}")
    lines.append("")
    lines.append("Corpus stats")
    lines.extend(collection_stats_lines(report))
    lines.append("")

    if report.compare:
        lines.append(f"Gold comparison against output/  (abs tol {ABS_TOL:g})")
        all_ok = True
        for name in ("idf", "tf", "tfidf"):
            if name not in report.compare:
                continue
            bucket = report.compare[name]
            status = "ok" if bucket.ok() else "MISMATCH"
            if not bucket.ok():
                all_ok = False
            lines.append(
                f"  {name:6}  {status:8}  "
                f"shared={bucket.shared_terms}  "
                f"missing={bucket.missing_in_computed}  "
                f"extra={bucket.extra_in_computed}  "
                f"mismatches={bucket.mismatches}  "
                f"max|Δ|={bucket.max_abs_delta:.3e}"
            )
        if all_ok and report.variant == "classic" and report.n_mode == "documents":
            lines.append(
                "  classic + documents matches the 2012 tables on this tree."
            )
        elif report.variant != "classic" or report.n_mode != "documents":
            lines.append(
                "  skipping a pass/fail claim: gold tables are classic / N=18."
            )
        lines.append("")

    lines.append("Top TF-IDF terms per document")
    for doc in report.documents:
        rows = report.top_terms.get(doc.name, [])
        lines.append(
            f"  {doc.name}  "
            f"({fmt_int(doc.kept_tokens)} tokens, "
            f"{fmt_int(len(doc.counts))} types)"
        )
        if not rows:
            lines.append("      (empty)")
            continue
        for term, score in rows:
            lines.append(f"      {score:12.8f}  {term}")
    lines.append("")
    lines.append(
        "See docs/benchmark.md for how to read this report and "
        "docs/algorithm.md for the arithmetic."
    )
    return "\n".join(lines) + "\n"


def report_to_json(report: BenchmarkReport) -> dict:
    return {
        "corpus": str(report.corpus),
        "variant": report.variant,
        "n_mode": report.n_mode,
        "n_used": report.n_used,
        "repeats": report.repeats,
        "best_times": report.best_times.as_dict(),
        "mean_total": report.mean_total,
        "documents": [
            {
                "name": d.name,
                "raw_bytes": d.raw_bytes,
                "word_count": d.word_count,
                "kept_tokens": d.kept_tokens,
                "types": len(d.counts),
            }
            for d in report.documents
        ],
        "vocab_size": len(report.idf),
        "compare": {
            name: {
                "gold_terms": b.gold_terms,
                "computed_terms": b.computed_terms,
                "shared_terms": b.shared_terms,
                "missing_in_computed": b.missing_in_computed,
                "extra_in_computed": b.extra_in_computed,
                "max_abs_delta": b.max_abs_delta,
                "mismatches": b.mismatches,
                "ok": b.ok(),
            }
            for name, b in report.compare.items()
        },
        "top_terms": {
            name: [{"term": t, "tfidf": s} for t, s in rows]
            for name, rows in report.top_terms.items()
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Personal in-memory TF-IDF benchmark for the Gutenberg toy "
            "corpus in this repository. Standard library only."
        ),
        epilog=(
            "Classic IDF is ln(N/df). Use --self-test for the three-document "
            "postcard in docs/algorithm.md. This script is personal study "
            "code; do not drop company sources into this tree."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    root = repo_root_from_script()
    parser.add_argument(
        "--corpus",
        type=Path,
        default=root / "gutenberg",
        help="Directory of one-document-per-file texts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "output",
        help="Checked-in Perl tables, used only by --compare-output.",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="Full pipeline runs; the report prints the fastest.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=8,
        help="How many highest TF-IDF terms to print per document.",
    )
    parser.add_argument(
        "--variant",
        choices=sorted(IDF_VARIANTS),
        default="classic",
        help="IDF formula. Only classic matches output/idf.txt.",
    )
    parser.add_argument(
        "--n-mode",
        choices=("documents", "perl-last-index"),
        default="documents",
        help="Collection size N. documents=18 here; perl-last-index is $#files.",
    )
    parser.add_argument(
        "--compare-output",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Diff IDF / TF / TF-IDF against the checked-in output/ tables.",
    )
    parser.add_argument(
        "--write-report",
        type=Path,
        default=None,
        help="Also write the text report to this path.",
    )
    parser.add_argument(
        "--write-json",
        type=Path,
        default=None,
        help="Also write a machine-readable report to this path.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the 3-document postcard and exit. Ignores --corpus.",
    )
    return parser


def run_benchmark(args: argparse.Namespace) -> BenchmarkReport:
    if args.repeats < 1:
        raise SystemExit("--repeats must be >= 1")
    if args.top < 0:
        raise SystemExit("--top must be >= 0")
    corpus = args.corpus
    if not corpus.is_dir():
        raise SystemExit(f"corpus directory not found: {corpus}")

    last: BenchmarkReport | None = None
    times: list[StageTimes] = []
    for _ in range(args.repeats):
        collection, read_s, tok_s = load_collection(corpus)
        idf, idf_s, n_used = compute_idf(collection, args.variant, args.n_mode)
        tfidf, prod_s = compute_tfidf(collection, idf)
        top, rank_s = rank_top_terms(tfidf, args.top)
        stage = StageTimes(
            read_files=read_s,
            tokenize_and_count=tok_s,
            compute_idf=idf_s,
            compute_tfidf=prod_s,
            rank_top_terms=rank_s,
        )
        times.append(stage)
        last = BenchmarkReport(
            corpus=corpus,
            n_mode=args.n_mode,
            variant=args.variant,
            n_used=n_used,
            repeats=args.repeats,
            times=times,
            documents=collection.documents,
            idf=idf,
            tfidf=tfidf,
            top_terms=top,
            df=collection.df,
        )

    assert last is not None
    if args.compare_output:
        last.compare = compare_against_output(last, args.output_dir)
    return last


def compare_failed(report: BenchmarkReport) -> bool:
    if report.variant != "classic" or report.n_mode != "documents":
        return False
    if not report.compare:
        return False
    return any(not bucket.ok() for bucket in report.compare.values())


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test()

    report = run_benchmark(args)
    text = format_report(report)
    sys.stdout.write(text)

    if args.write_report is not None:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        args.write_report.write_text(text, encoding="utf-8")
    if args.write_json is not None:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(
            json.dumps(report_to_json(report), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if compare_failed(report):
        sys.stderr.write(
            "benchmark: classic/documents numbers did not match output/\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
