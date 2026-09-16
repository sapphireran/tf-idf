# How to read `output/`

Every generated table is UTF-8 (ASCII in practice) TSV: `term<TAB>value`.
Terms are lowercased. Files under `output/tf/` and `output/tfidf/` are sorted
**A–Z by term**, not by score.

## `output/tf/<document>.txt`

```
emma	0.002951...
the	0.0481...
```

Column 2 is `count / tokens` for that document only. It does not know about
other books.

Sanity checks:

- Most values are tiny (`1e-5` to `1e-2`). A 158k-word novel makes even a
  400-count name look small.
- The largest TF terms are usually function words (`the`, `and`, `of`, `to`).
- Summing column 2 over a file is approximately `1`. It can be slightly less
  if `$word_count` included empty split pieces that never entered `%tf`.

```bash
# largest raw TF in Emma (function words will win)
sort -t$'\t' -k2,2nr output/tf/austen-emma.txt | head
```

## `output/df.txt`

```
word 	 #docs it exists in 	 doc names
emma	2	austen-persuasion.txt, austen-emma.txt,
the	18	chesterton-brown.txt, whitman-leaves.txt, ...
```

- Line 1 is a header. The extra spaces around the tabs are literal.
- Column 2 is integer DF in `1 … 18`.
- Column 3 is a comma-separated list of filenames with a trailing `", "`.
  Order is Perl hash order from the 2012 run; do not interpret it.

`output/df-sorted.txt` is a derived dump of the same information (very large).
Prefer `df.txt` plus `sort` when you need another order.

## `output/idf.txt`

```
emma	2.19722457733622
harriet	2.89037175789616
the	0
```

No header. Column 2 is `ln(18 / df)`. Look up a few anchors if you suspect a
file got regenerated with a different `N`:

| Term | Expected IDF in this checkout |
| --- | --- |
| any `df = 1` term, e.g. `harriet` | `2.89037175789616` |
| any `df = 2` term, e.g. `emma` | `2.19722457733622` |
| any `df = 18` term, e.g. `the` | `0` |

One historical typo lives on line 50450: `thatyou` has IDF `2.89037175789616y`
(a trailing `y`). Parsers that `float()` the column will throw; strip
non-numeric suffix if you need that row. See
[`tokenizer-and-quirks.md`](tokenizer-and-quirks.md).

## `output/tfidf/<document>.txt`

```
emma	0.0104321493626056
the	0
```

Column 2 is `tf * idf`. Zero means “this term occurs in all 18 documents,” not
“the term is absent.” Absent terms are simply missing rows.

### Ranking without getting fooled by scientific notation

```bash
# GNU sort, numeric, descending
sort -t$'\t' -k2,2nr output/tfidf/austen-emma.txt | head -12
```

A **lexical** sort of column 2 orders the strings `9e-05`, `8e-03`, `0.01` by
characters, not magnitude. That is why a naive `sort -k2 -r` looks like the
top of *Emma* is `fortune` / `acquainted` instead of `emma`.

Python is unambiguous:

```bash
python3 examples/rank_top_terms.py --dir output/tfidf --file austen-emma.txt --k 12
```

## How many terms get zeroed?

In `output/tfidf/austen-emma.txt`, **220** terms have TF-IDF exactly `0`
(`examples/rank_top_terms.py --zeros`). They are the vocabulary intersection
of all 18 files: `a`, `about`, `after`, `and`, `the`, plus a surprising
number of milder words that just happen to appear everywhere in this sample
(`age`, `alone`, `angry`, `bed`, …).

Zero is a **corpus accident**. Add a 19th document that never says `angry`
and `angry` would suddenly have nonzero IDF in *Emma*.

## Cross-checking TF × IDF by hand

Pick a term that exists in both tables:

```bash
# TF in Emma
awk -F'\t' '$1=="emma" {print $2}' output/tf/austen-emma.txt

# IDF (corpus)
awk -F'\t' '$1=="emma" {print $2}' output/idf.txt

# stored product
awk -F'\t' '$1=="emma" {print $2}' output/tfidf/austen-emma.txt
```

You should see `tf * idf ≈ 0.0104321493626056`. Floating-point text dumps
will not match a fresh `print` to the last bit; comparing to ~10 significant
digits is enough.

## When a “surprising” top term is correct

| Observation | Usual cause |
| --- | --- |
| `macb` beats `macbeth` | Speech prefix is more frequent **and** `df = 1` |
| `mr` / `mrs` still rank in Austen | They miss several non-Austen files, so IDF > 0 |
| `unto` tops the KJV list | Extremely common in that file, only `df = 6` |
| `ebook` appears in Chesterton | Gutenberg header survived in that one transcription |
| `o` ranks in Whitman | Vocative “O” is a real stylistic tic; `df = 12` so IDF is small but TF is huge |
| Short book has larger peak scores | Same name repetition, smaller `tokens(d)` |

Longer narrative readings: [`../examples/gutenberg-top-terms.md`](../examples/gutenberg-top-terms.md).
