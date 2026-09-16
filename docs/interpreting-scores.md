# Interpreting the score tables

All personal notes below assume the **checked-in** `output/` snapshot
(`N = 18`, natural-log IDF, length-normalized TF). If you regenerate the
tables, reread [perl-pipeline.md](perl-pipeline.md) first.

## Reading one row

A line in `output/tfidf/carroll-alice.txt`:

```
alice	0.025956780390307
```

Means: after this tokenizer, the string `alice` accounts for about 1.45% of
Alice's tokens (`output/tf/carroll-alice.txt`) and appears in 3 of 18 books
(`output/df.txt`), so it is multiplied by `ln(18/3) ≈ 1.792`.

A line like:

```
a	0
```

Means the term's IDF was 0 (present in every book). TF is *not* zero —
`output/tf/carroll-alice.txt` has `a	0.02359`. The product is zero. The
row is still written because pass 2 multiplies every TF term it sees.

## Comparing two terms in the same book

Inside one file, a higher TF-IDF means "more surprising relative to this
collection." It does not mean "more important to the plot."

| Term in Alice | Why it ranks where it does |
| --- | --- |
| `alice` | High TF, moderate IDF (`df = 3`). Wins the file. |
| `gryphon` | Modest TF, high IDF (`df = 2`, Carroll + Milton). Second place. |
| `rabbit` | Decent TF, but `df = 6` (Burgess et al. also have rabbits). Mid-pack. |
| `the` | Highest TF in most English prose; IDF 0. Dead last (tied with other collection-wide words). |

Cross-book comparison of raw TF-IDF values is shakier. Blake's top score and
Melville's top score live in vectors of very different density. Use cosine
similarity (`examples/compare_documents.py`) if the question is "which books
look alike," not "which book has the bigger `whale` number."

## Comparing two books

`examples/compare_documents.py` builds a sparse vector per file: each term
is a dimension, the value is the checked-in TF-IDF. Cosine similarity is

```
cos(u, v) = (u · v) / (||u|| ||v||)
```

Terms that are 0 in both books do not appear in either file and never enter
the dot product. Terms that are 0 in one book (absent from that TF table)
contribute nothing. That is ordinary sparse cosine.

Expect, qualitatively:

- Austen ↔ Austen and Chesterton ↔ Chesterton: high.
- Shakespeare ↔ Shakespeare: high, partly because they share `haue` / `vpon`
  / `vs` / `doe`.
- Alice ↔ Bible: low.
- *Moby-Dick* ↔ Whitman: middling — both are 19th-century American and
  share some sea / body vocabulary, but the character names are unique.

If a pair looks "too similar," dump the overlapping high terms with:

```bash
python3 examples/compare_documents.py --a shakespeare-hamlet --b shakespeare-macbeth --show-overlap 20
```

## Ranking without getting tricked

The TF and TF-IDF files are **alphabetically** sorted. The visually first
rows are not the most important.

```bash
# Wrong on many systems: scientific notation sorts as text or as 9.89
sort -t$'\t' -k2 -nr output/tfidf/carroll-alice.txt | head

# Right: parse as float
python3 examples/top_terms.py --doc carroll-alice --n 20
```

`sort -g` (general numeric) also works on GNU sort. macOS `/usr/bin/sort`
is not GNU by default.

## Useful filters when skimming top terms

I keep these in mind when reading `top_terms.py` output:

1. **Drop pure digits** if the file is `bible-kjv.txt`.
2. **Drop 3–4 letter all-token speaker codes** if the file is Shakespeare
   (`ham`, `macb`, `hor`, `qu`, `pol`).
3. **Treat possessives as separate terms.** `alices`, `emmas`, `harriets`
   are not errors; the apostrophe was deleted.
4. **Treat smashed hyphenation as leftover.** `waistcoatpocket` will never
   merge with `waistcoat` + `pocket` unless the tokenizer changes.

None of these filters are applied in `output/`. They are reading advice.

## File sizes and when to grep vs load

`output/idf.txt` and `output/df.txt` have on the order of 57k terms (the
union vocabulary). A single novel's TF file is a few thousand rows; the
Bible's is much larger. Grep is fine for one term:

```bash
grep -h $'^whale\t' output/idf.txt output/df.txt
grep $'^whale\t' output/tf/melville-moby_dick.txt
grep $'^whale\t' output/tfidf/melville-moby_dick.txt
```

For top-N or cosine, load the file in Python. The example scripts stream
linewise and keep only floats they can parse, so a header-less TSV is
enough.

## Reproducing a single number

Given term `t` and book `b`:

```
tf    = column 2 of output/tf/b.txt
idf   = column 2 of output/idf.txt
tfidf = tf * idf
      = column 2 of output/tfidf/b.txt
```

If `tf * idf` disagrees with the TF-IDF file, pass 2 was run against a
different `idf.txt` than the one on disk. The snapshot in this repo is
internally consistent for the terms I checked (`alice`, `whale`, `emma`,
`the`).
