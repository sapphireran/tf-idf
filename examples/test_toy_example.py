#!/usr/bin/env python3
"""Check the toy corpus against the hand calculation in worked-example.md."""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tfidf_mini import analyze_directory, tokenize  # noqa: E402

TOY = Path(__file__).resolve().parent / "toy-corpus"
EPS = 1e-12

LN4 = math.log(4)          # unique terms
LN2 = math.log(2)          # df = 2
LN43 = math.log(4 / 3)     # df = 3


def almost(actual: float, expected: float) -> None:
    if abs(actual - expected) > EPS:
        raise AssertionError(f"{actual!r} != {expected!r} (eps={EPS})")


def test_tokenizer_is_a_noop_on_the_toy_lines() -> None:
    for name, text in {
        "cats.txt": "the cat sat on the mat the cat likes fish",
        "dogs.txt": "the dog sat on the log the dog likes bones",
        "space.txt": "rockets fly to the moon astronauts like space",
        "pets.txt": "the cat and the dog play on the mat",
    }.items():
        fields = tokenize(text)
        assert fields == text.split(" "), name
        assert all(fields), f"unexpected empty token in {name}"


def test_hand_calculation() -> None:
    result = analyze_directory(TOY, faithful=True)
    assert result["n_docs"] == 4
    assert set(result["tf"]) == {"cats.txt", "dogs.txt", "space.txt", "pets.txt"}

    cats_tf = result["tf"]["cats.txt"]
    almost(cats_tf["the"], 0.3)
    almost(cats_tf["cat"], 0.2)
    almost(cats_tf["fish"], 0.1)
    assert len(tokenize((TOY / "cats.txt").read_text())) == 10

    dogs_tf = result["tf"]["dogs.txt"]
    almost(dogs_tf["the"], 0.3)
    almost(dogs_tf["dog"], 0.2)
    almost(dogs_tf["bones"], 0.1)

    space_tf = result["tf"]["space.txt"]
    assert set(space_tf) == {
        "rockets",
        "fly",
        "to",
        "the",
        "moon",
        "astronauts",
        "like",
        "space",
    }
    for weight in space_tf.values():
        almost(weight, 0.125)

    pets_tf = result["tf"]["pets.txt"]
    almost(pets_tf["the"], 3 / 9)
    almost(pets_tf["play"], 1 / 9)

    idf = result["idf"]
    almost(idf["the"], 0.0)
    almost(idf["on"], LN43)
    almost(idf["cat"], LN2)
    almost(idf["dog"], LN2)
    almost(idf["likes"], LN2)
    almost(idf["fish"], LN4)
    almost(idf["bones"], LN4)
    almost(idf["play"], LN4)
    almost(idf["and"], LN4)
    # like (space) is not likes (cats/dogs)
    almost(idf["like"], LN4)
    assert result["df"]["likes"] == {"cats.txt", "dogs.txt"}
    assert result["df"]["like"] == {"space.txt"}

    cats = result["tfidf"]["cats.txt"]
    almost(cats["the"], 0.0)
    almost(cats["cat"], 0.2 * LN2)
    almost(cats["fish"], 0.1 * LN4)
    almost(cats["cat"], cats["fish"])  # the documented tie
    almost(cats["on"], 0.1 * LN43)
    winners = {t for t, w in cats.items() if abs(w - cats["cat"]) <= EPS}
    assert winners == {"cat", "fish"}

    dogs = result["tfidf"]["dogs.txt"]
    almost(dogs["dog"], 0.2 * LN2)
    almost(dogs["log"], 0.1 * LN4)
    almost(dogs["bones"], 0.1 * LN4)
    assert {t for t, w in dogs.items() if abs(w - dogs["dog"]) <= EPS} == {
        "dog",
        "log",
        "bones",
    }

    space = result["tfidf"]["space.txt"]
    almost(space["the"], 0.0)
    for term in ("rockets", "moon", "astronauts", "space"):
        almost(space[term], 0.125 * LN4)

    pets = result["tfidf"]["pets.txt"]
    almost(pets["the"], 0.0)
    almost(pets["and"], (1 / 9) * LN4)
    almost(pets["play"], (1 / 9) * LN4)
    almost(pets["cat"], (1 / 9) * LN2)
    assert pets["and"] > pets["cat"]


def test_faithful_and_clean_agree_without_empty_fields() -> None:
    faithful = analyze_directory(TOY, faithful=True)
    clean = analyze_directory(TOY, faithful=False)
    for name in faithful["tf"]:
        assert faithful["tf"][name] == clean["tf"][name]
        assert faithful["tfidf"][name] == clean["tfidf"][name]


def test_empty_field_changes_only_the_faithful_denominator() -> None:
    # Leading space survives collapse and becomes an empty split field, as in Perl.
    texts = {"a.txt": " cat dog", "b.txt": "moon"}
    from tfidf_mini import analyze_texts

    faithful = analyze_texts(texts, faithful=True)
    clean = analyze_texts(texts, faithful=False)
    assert tokenize(" cat dog") == ["", "cat", "dog"]
    almost(faithful["tf"]["a.txt"]["cat"], 1 / 3)
    almost(clean["tf"]["a.txt"]["cat"], 1 / 2)
    assert faithful["tf"]["a.txt"]["cat"] != clean["tf"]["a.txt"]["cat"]


def test_cats_are_closer_to_pets_than_to_space() -> None:
    from tfidf_mini import cosine

    result = analyze_directory(TOY, faithful=True)
    vec = result["tfidf"]
    cats_pets = cosine(vec["cats.txt"], vec["pets.txt"])
    cats_space = cosine(vec["cats.txt"], vec["space.txt"])
    dogs_pets = cosine(vec["dogs.txt"], vec["pets.txt"])
    assert cats_pets > cats_space
    assert dogs_pets > cats_space
    almost(cats_space, 0.0)


def test_fifth_document_breaks_the_cat_fish_tie() -> None:
    from tfidf_mini import analyze_texts, load_corpus

    extra = TOY / "extra" / "more-cats.txt"
    before = analyze_directory(TOY, faithful=True)
    almost(before["tfidf"]["cats.txt"]["cat"], before["tfidf"]["cats.txt"]["fish"])

    texts = load_corpus(TOY)
    texts[extra.name] = extra.read_text(encoding="utf-8")
    after = analyze_texts(texts, faithful=True)
    assert after["n_docs"] == 5
    assert after["tfidf"]["cats.txt"]["cat"] != after["tfidf"]["cats.txt"]["fish"]
    assert after["tfidf"]["cats.txt"]["cat"] > after["tfidf"]["cats.txt"]["fish"]
    assert "kitten" in after["tfidf"]["more-cats.txt"]


def test_run_toy_example_cli() -> None:
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parent / "run_toy_example.py")],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "N documents: 4" in proc.stdout
    assert "cat            0.138629436112" in proc.stdout
    assert "fish           0.138629436112" in proc.stdout


def test_add_a_document_cli() -> None:
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parent / "add_a_document.py")],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "tie broken" in proc.stdout
    assert "cat now leads" in proc.stdout


def main() -> int:
    tests = [
        test_tokenizer_is_a_noop_on_the_toy_lines,
        test_hand_calculation,
        test_faithful_and_clean_agree_without_empty_fields,
        test_empty_field_changes_only_the_faithful_denominator,
        test_cats_are_closer_to_pets_than_to_space,
        test_fifth_document_breaks_the_cat_fish_tie,
        test_run_toy_example_cli,
        test_add_a_document_cli,
    ]
    for fn in tests:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"passed {len(tests)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
