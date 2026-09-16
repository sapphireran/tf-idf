#!/usr/bin/env python3
"""Assert the tiny-corpus script matches the hand calculation.

No third-party test runner. Exit 0 on success, 1 on the first mismatch.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import compute_tfidf  # noqa: E402

N_DOCS = 4
LN_4 = math.log(4)
LN_2 = math.log(2)
LN_4_OVER_3 = math.log(4 / 3)


def almost(left: float, right: float, places: int = 6) -> None:
    if round(left - right, places) != 0:
        raise AssertionError(f"{left!r} != {right!r} (rounded to {places} dp)")


def test_tokenize_strips_punctuation_and_newlines() -> None:
    tokens = compute_tfidf.tokenize("Cats chase mice. Cats sleep on warm mats.\n")
    assert tokens == ["cats", "chase", "mice", "cats", "sleep", "on", "warm", "mats"]
    smashed = compute_tfidf.tokenize("Alice's waistcoat-pocket, don't.")
    assert smashed == ["alices", "waistcoatpocket", "dont"]


def test_tables_match_hand_calc() -> None:
    documents = compute_tfidf.load_documents(HERE / "docs")
    by_name = {doc.name: doc for doc in documents}
    assert set(by_name) == {"cats.txt", "dogs.txt", "space.txt", "kitchen.txt"}
    assert by_name["cats.txt"].n_tokens == 8
    assert by_name["dogs.txt"].n_tokens == 8
    assert by_name["space.txt"].n_tokens == 9
    assert by_name["kitchen.txt"].n_tokens == 9

    df = compute_tfidf.document_frequency(documents)
    idf = compute_tfidf.inverse_document_frequency(df, len(documents))
    tfidf = compute_tfidf.tfidf_table(documents, idf)

    assert df["cats"] == 2
    assert df["chase"] == 3
    assert df["dogs"] == 1
    assert df["in"] == 2
    assert df["the"] == 1
    assert df["stars"] == 1
    assert df["bread"] == 1
    assert len(documents) == N_DOCS

    almost(idf["dogs"], LN_4)
    almost(idf["cats"], LN_2)
    almost(idf["chase"], LN_4_OVER_3)
    almost(idf["warm"], LN_4_OVER_3)

    almost(by_name["cats.txt"].tf["cats"], 2 / 8)
    almost(by_name["dogs.txt"].tf["dogs"], 2 / 8)
    almost(by_name["space.txt"].tf["stars"], 2 / 9)
    almost(by_name["kitchen.txt"].tf["bread"], 2 / 9)

    almost(tfidf["cats.txt"]["cats"], (2 / 8) * LN_2)
    almost(tfidf["cats.txt"]["mice"], (1 / 8) * LN_4)
    almost(tfidf["cats.txt"]["mats"], (1 / 8) * LN_4)
    almost(tfidf["cats.txt"]["cats"], tfidf["cats.txt"]["mice"])

    almost(tfidf["dogs.txt"]["dogs"], (2 / 8) * LN_4)
    almost(tfidf["space.txt"]["stars"], (2 / 9) * LN_4)
    almost(tfidf["kitchen.txt"]["bread"], (2 / 9) * LN_4)
    almost(tfidf["kitchen.txt"]["the"], (1 / 9) * LN_4)
    almost(tfidf["kitchen.txt"]["chase"], (1 / 9) * LN_4_OVER_3)

    almost(tfidf["cats.txt"]["cats"], 0.173287)
    almost(tfidf["dogs.txt"]["dogs"], 0.346574)
    almost(tfidf["space.txt"]["stars"], 0.308065)
    almost(tfidf["kitchen.txt"]["bread"], 0.308065)


def main() -> int:
    try:
        test_tokenize_strips_punctuation_and_newlines()
        test_tables_match_hand_calc()
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        return 1
    print("tiny-corpus hand-calc checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
