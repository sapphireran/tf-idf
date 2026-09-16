# Public-domain excerpts

Three short slices copied from the Gutenberg files already in this repo. They exist so you can watch TF-IDF work on a collection you can read in one sitting.

| file | source in `gutenberg/` | roughly about |
| --- | --- | --- |
| `alice-opening.txt` | `carroll-alice.txt`, rabbit-hole opening | Alice, the Rabbit, a book without pictures |
| `moby-cetology.txt` | `melville-moby_dick.txt`, Ishmael + sperm-whale proclamation | Ishmael, Greenland whale vs sperm whale |
| `macbeth-witches.txt` | `shakespeare-macbeth.txt`, I.i–I.ii | witches, Macbeth, Early Modern spelling |

These are not substitutes for the 18-book run. They are a middle step between the six-word toy corpus and *Moby-Dick*.

## Run

```bash
python3 examples/python/tfidf_example.py \
  --input-dir examples/excerpts \
  --output-dir /tmp/excerpt-tfidf

python3 examples/python/extract_top_terms.py /tmp/excerpt-tfidf/tfidf/alice-opening.txt -n 12
python3 examples/python/extract_top_terms.py /tmp/excerpt-tfidf/tfidf/moby-cetology.txt -n 12
python3 examples/python/extract_top_terms.py /tmp/excerpt-tfidf/tfidf/macbeth-witches.txt -n 12
```

## What you should see

`N = 3` and only `*.txt` files count (this README is not a document). IDF is harsh: a word in all three excerpts is zeroed. A word that misses even one file keeps `ln(3/2)` or `ln(3/1)`.

That is enough to beat `the`, but it is **not** enough to make proper names win automatically. A run of the committed files produces:

| file | TF head | TF-IDF head | names / topical nouns in the top 15 |
| --- | --- | --- | --- |
| `alice-opening.txt` | the, it, a, to | **she**, **her**, alice, very, rabbit | alice #3, rabbit #7, book #12 |
| `moby-cetology.txt` | the, and, of, … | **whale**, **sperm**, are, books, greenland | whale #1, sperm #2, greenland #9 |
| `macbeth-witches.txt` | the, and, … | **1**, **king**, 2, 3, bloody, macbeth | speaker numbers, then macbeth / thunder / lightning |

Alice's opening is full of `she` / `her`; the other two excerpts almost never use those pronouns, so they look as "distinctive" as the heroine. On the 18-book shelf, `she` has IDF 0 and `alice` is first. The excerpt collection is the middle lesson: **IDF measures rarity in the shelf you built**, not an English stopword list.

Melville's slice is already noun-heavy (`whale` six times, `sperm` four), so topical words win even at `N = 3`. Macbeth's slice still leaks speaker numbers (`1`, `2`, `3`) the same way the full play leaks `macb`.

Compare `--tf` on `alice-opening.txt`: `the` / `it` / `a` / `to` lead. TF-IDF at least lets `alice` and `rabbit` into the head of the list. The 18-book tables in [../../docs/interpreting-results.md](../../docs/interpreting-results.md) are what happens when `N` is large enough that pronouns stop being rare.

Exact floats for the committed excerpts are in [sample-rankings.md](sample-rankings.md).

## Provenance

Text is public-domain Project Gutenberg material already stored under `gutenberg/`. Line breaks follow those files. Do not replace these excerpts with copyrighted novels.
