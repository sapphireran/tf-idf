# How to read `output/`

The committed `output/` tree is a snapshot of a 2012 run against the 18
Gutenberg files. You do not need to rerun Perl to study it.

## Files

| Path | Columns | Sort order |
| --- | --- | --- |
| `output/tf/<file>` | `term`, normalized TF | alphabetical by term |
| `output/idf.txt` | `term`, `ln(N/df)` | alphabetical by term |
| `output/df.txt` | `term`, df, filename list | alphabetical; has a header row |
| `output/df-sorted.txt` | same as `df.txt` | extra artifact, not from the scripts |
| `output/tfidf/<file>` | `term`, `tf * idf` | alphabetical by term |

All data files are tab-separated. Decimal numbers are Perl's default
stringification, so you will see values like `2.89037175789616` and
occasional scientific notation for tiny products.

## Zeros are not missing data

A tf*idf of `0` means `idf = 0`, which means the term appeared in all
18 documents. In `output/tfidf/blake-poems.txt` the row

```
a	0
```

is the word `a`, not a broken line. The same file still lists `thel`
near `0.005581` because *The Book of Thel* is in that file and almost
nowhere else.

## IDF ceiling

Unique terms have `idf = ln(18) ≈ 2.89037175789616`. That constant
shows up constantly at the top of `output/idf.txt` (including for
tokens that are just numbers). High IDF is not praise. It only says
"this string was rare in the collection."

Spot checks against the formula, using `df.txt` and `idf.txt`:

| term | df | expected idf | stored idf |
| --- | ---: | ---: | ---: |
| `the` | 18 | `ln(18/18) = 0` | `0` |
| `whale` | 6 | `ln(18/6) = ln(3) ≈ 1.0986` | `1.09861228866811` |
| `alice` | 3 | `ln(18/3) = ln(6) ≈ 1.7918` | `1.79175946922805` |
| `emma` | 2 | `ln(18/2) = ln(9) ≈ 2.1972` | `2.19722457733622` |
| `buster` | 1 | `ln(18/1) ≈ 2.8904` | `2.89037175789616` |

Those identities are how we know the snapshot used **N = 18**, not the
`$#files` last-index value.

## Ranking the snapshot

Alphabetical TSV is the wrong shape for skimming. From the repo root:

```bash
python3 scripts/rank_precomputed_tfidf.py --top 10
python3 scripts/rank_precomputed_tfidf.py --only melville-moby_dick.txt
python3 scripts/rank_precomputed_tfidf.py --only shakespeare-hamlet.txt --min-length 4
```

`--min-length 4` is a blunt way to hide some speaker tags (`ham`,
`qu`, `pol`) without introducing a real stopword list. It also hides
`o` in Whitman.

Worked rankings for every file are in
[gutenberg-top-terms.md](gutenberg-top-terms.md).

## Joining TF, IDF, and TF-IDF by hand

Pick a term and a file, for example `alice` in `carroll-alice.txt`:

1. Read `output/tf/carroll-alice.txt` and find the `alice` row. That is
   normalized TF.
2. Read `output/idf.txt` for `alice` (`≈ 1.7918`).
3. The product should match `output/tfidf/carroll-alice.txt`.

If you want a term that is easier to reason about without opening huge
files, use the tiny corpus under `examples/tiny-output/` instead. Those
TSVs are short enough to read top to bottom.

## What not to treat as ground truth

- The tables are not cosine-normalized document vectors. You cannot
  compare `0.04` in Burgess to `0.01` in Austen as "four times more
  about this word" across books of different lengths without more
  work. Inside **one** file, the order is meaningful.
- Tokens are not lemmas. `whale` and `whales` are two rows.
- A handful of IDF lines in the snapshot look corrupted (a stray
  letter glued to a float). The ranking helper skips values that do
  not parse as floats. Treat that as a reason not to over-trust a
  2012 dump, not as something this docs pass silently rewrote.
