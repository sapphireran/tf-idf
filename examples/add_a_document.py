#!/usr/bin/env python3
"""Show how adding one document rewrites every idf — and some rankings.

Baseline: the four-file toy corpus.
Perturbation: examples/toy-corpus/extra/more-cats.txt
    "the cat ate the fish the kitten likes cream"

That fifth file mentions cat *and* fish, so the cats.txt tie
(cat tf-idf == fish tf-idf) must break. See examples/collection-design.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tfidf_mini import (  # noqa: E402
    analyze_texts,
    format_float,
    load_corpus,
    ranked,
)

TOY = Path(__file__).resolve().parent / "toy-corpus"
EXTRA = TOY / "extra" / "more-cats.txt"


def show_idf(title: str, result: dict, terms: tuple[str, ...]) -> None:
    print(title)
    print(f"  N = {result['n_docs']}")
    for term in terms:
        df = len(result["df"].get(term, ()))
        idf = result["idf"].get(term)
        idf_s = format_float(idf) if idf is not None else "missing"
        print(f"  {term:<10} df={df}  idf={idf_s}")


def show_top(name: str, table: dict, n: int = 4) -> None:
    print(f"  {name}:")
    for term, weight in ranked(table, n):
        print(f"    {term:<10} {format_float(weight)}")


def main() -> int:
    base_texts = load_corpus(TOY)
    # load_corpus skips extra/ because it only reads files, not nested dirs —
    # extra/ is a subdirectory, so the baseline stays four documents.
    before = analyze_texts(base_texts, faithful=True)

    with_extra = dict(base_texts)
    with_extra[EXTRA.name] = EXTRA.read_text(encoding="utf-8")
    after = analyze_texts(with_extra, faithful=True)

    terms = ("the", "cat", "fish", "dog", "rockets", "kitten", "cream")
    print("before (4 documents)")
    print("--------------------")
    show_idf("idf", before, terms)
    print("cats.txt ranking")
    show_top("cats.txt", before["tfidf"]["cats.txt"])
    print("pets.txt ranking")
    show_top("pets.txt", before["tfidf"]["pets.txt"])

    print()
    print("after adding more-cats.txt")
    print("--------------------------")
    print(f"  extra text: {EXTRA.read_text(encoding='utf-8').strip()!r}")
    show_idf("idf", after, terms)
    print("cats.txt ranking")
    show_top("cats.txt", after["tfidf"]["cats.txt"])
    print("more-cats.txt ranking")
    show_top("more-cats.txt", after["tfidf"]["more-cats.txt"])
    print("pets.txt ranking")
    show_top("pets.txt", after["tfidf"]["pets.txt"])

    cat_before = before["tfidf"]["cats.txt"]["cat"]
    fish_before = before["tfidf"]["cats.txt"]["fish"]
    cat_after = after["tfidf"]["cats.txt"]["cat"]
    fish_after = after["tfidf"]["cats.txt"]["fish"]
    print()
    print("the cats.txt tie")
    print("----------------")
    print(f"  before: cat={format_float(cat_before)}  fish={format_float(fish_before)}")
    print(f"  after:  cat={format_float(cat_after)}  fish={format_float(fish_after)}")
    if cat_before == fish_before and cat_after != fish_after:
        winner = "cat" if cat_after > fish_after else "fish"
        print(f"  tie broken; {winner} now leads inside cats.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
