# What changes when the shelf grows

Same formulas, three collection sizes. This is the reason the repo has a toy corpus, a three-excerpt folder, *and* the 18 Gutenberg files.

## N = 3, six-word files

[tiny-corpus walkthrough](../examples/tiny-corpus/walkthrough.md)

Every distinctive noun has `df = 1` and the same TF-IDF (`ln(3)/6`). Shared words are exactly 0. The ranking is a cast list because there is no other vocabulary.

Lesson: TF-IDF can separate `cat` / `dog` / `bird` when documents are short, balanced, and share a template sentence.

## N = 3, a few hundred tokens each

[excerpts](../examples/excerpts/README.md)

Documents are real prose, still only three of them. Words that happen to miss one file get a large IDF even when they are pronouns or the numeral `1`.

| collection | Alice-file winner |
| --- | --- |
| tiny corpus (if Alice were a file named `cats`) | the unique nouns |
| excerpts | `she` / `her`, then `alice` |
| 18 Gutenberg books | `alice` |

Lesson: a small heterogeneous shelf makes **accidental** rarity look like aboutness. `she` is not "what the rabbit-hole chapter is about." It is "a word the other two excerpts did not use."

## N = 18, full books

[interpreting-results.md](interpreting-results.md)

Function words reach `df = 18` and drop to 0. Proper names and topical nouns keep enough TF to win even when `df` is 2–6 (`alice`, `whale`, `ahab`). New failure modes appear: speech prefixes, Early Modern spelling, catalog digits.

Lesson: IDF needs a shelf that is **large enough for stopwords to become common** and **mixed enough for names to stay rare**. Eighteen public-domain books is a sweet spot for a laptop experiment. It is still a toy relative to a web index.

## A single term across the three shelves

There is no `alice` in the tiny corpus. Invent one: add the word `alice` once to `cats.txt` and nowhere else.

| shelf | df(alice) | N | idf(alice) | what TF has to do |
| --- | --- | --- | --- | --- |
| tiny + one `alice` | 1 | 3 | ln(3) ≈ 1.099 | one occurrence in 6 tokens is already huge |
| excerpts | 1 | 3 | ln(3) ≈ 1.099 | must beat `she` (9 occurrences in 313 tokens) |
| Gutenberg | 3 | 18 | ln(6) ≈ 1.792 | 0.0145 TF is enough to finish first |

IDF is *higher* on the big shelf (`1.79` vs `1.10`) because 3/18 is rarer than 1/3. TF is *lower* because the book is longer. The product still puts `alice` first only when the competing high-TF words have been zeroed by a large `df`.

## Practical rule for this repo

If a ranking looks like English instead of a cast list, check `N` and `df` before blaming the formula.

```bash
python3 examples/python/extract_top_terms.py output/tfidf/carroll-alice.txt -n 5
grep -w '^she' output/idf.txt
grep -w '^alice' output/idf.txt
```

On the committed run, `she` is `0` and `alice` is `1.79175946922805`.
